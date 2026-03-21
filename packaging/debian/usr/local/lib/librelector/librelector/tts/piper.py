"""Piper TTS engine – offline neural voices.

Piper (https://github.com/rhasspy/piper) is a fast, local neural TTS engine.
It is invoked as a subprocess:  echo "text" | piper --model voice.onnx --output_raw | aplay

Word-level timing is approximated from audio duration / word count because
Piper's standard CLI does not expose phoneme timestamps.  When Piper JSON
output mode becomes stable this module can be upgraded.
"""
from __future__ import annotations

import io
import json
import logging
import re
import shutil
import subprocess
import threading
import time
from pathlib import Path
from typing import Optional

from .base import TTSEngine, TTSState

logger = logging.getLogger(__name__)


class PiperEngine(TTSEngine):
    """TTS engine backed by the Piper binary."""

    def __init__(self, model_path: str | Path, config_path: Optional[str | Path] = None):
        """
        Parameters
        ----------
        model_path:
            Path to the `.onnx` Piper voice model.
        config_path:
            Path to the `.onnx.json` config file.  Defaults to
            ``model_path`` with `.json` appended.
        """
        super().__init__()
        self.model_path = Path(model_path)
        self.config_path = Path(config_path) if config_path else self.model_path.with_suffix(".onnx.json")
        self._proc: Optional[subprocess.Popen] = None
        self._play_proc: Optional[subprocess.Popen] = None
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._pause_event.set()  # not paused initially

    # ── TTSEngine interface ──────────────────────────────────────────────────

    def is_available(self) -> bool:
        """Check that `piper` binary and model file exist."""
        piper_bin = shutil.which("piper") or shutil.which("piper-tts")
        return bool(piper_bin and self.model_path.exists())

    def speak(self, text: str, start_sentence: int = 0) -> None:
        self.stop()
        self._stop_event.clear()
        self._pause_event.set()
        self._set_state(TTSState.PLAYING)

        self._thread = threading.Thread(
            target=self._run,
            args=(text, start_sentence),
            daemon=True,
            name="PiperEngine-speak",
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        self._pause_event.set()   # unblock if paused
        self._kill_procs()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
        self._set_state(TTSState.STOPPED)

    def pause(self) -> None:
        if self.state == TTSState.PLAYING:
            self._pause_event.clear()
            self._kill_procs()
            self._set_state(TTSState.PAUSED)

    def resume(self) -> None:
        if self.state == TTSState.PAUSED:
            self._set_state(TTSState.PLAYING)
            self._pause_event.set()

    # ── internal ─────────────────────────────────────────────────────────────

    def _piper_bin(self) -> str:
        return shutil.which("piper") or shutil.which("piper-tts") or "piper"

    def _kill_procs(self) -> None:
        for proc in (self._proc, self._play_proc):
            if proc and proc.poll() is None:
                try:
                    proc.terminate()
                    proc.wait(timeout=1)
                except Exception:
                    try:
                        proc.kill()
                    except Exception:
                        pass
        self._proc = None
        self._play_proc = None

    def _run(self, text: str, start_sentence: int) -> None:
        """Background thread: split text into sentences and speak each one."""
        from ..epub.parser import _split_sentences  # avoid circular at module level

        sentences = _split_sentences(text)
        if start_sentence:
            sentences = sentences[start_sentence:]

        for idx, sentence in enumerate(sentences):
            if self._stop_event.is_set():
                break

            # Wait while paused
            self._pause_event.wait()
            if self._stop_event.is_set():
                break

            global_idx = idx + start_sentence
            self._emit_sentence(global_idx)

            self._speak_sentence(sentence, global_idx)

        if not self._stop_event.is_set():
            self._set_state(TTSState.IDLE)
            self._emit_finished()

    def _speak_sentence(self, sentence: str, sentence_idx: int) -> None:
        """Synthesise and play one sentence, emitting word events."""
        piper = self._piper_bin()
        cmd_piper = [
            piper,
            "--model", str(self.model_path),
            "--output_raw",
        ]
        if self.config_path.exists():
            cmd_piper += ["--config", str(self.config_path)]

        # Length factor: adjust for speed (Piper supports --length_scale)
        length_scale = 1.0 / self._speed
        cmd_piper += ["--length_scale", f"{length_scale:.2f}"]

        # aplay: play raw 16-bit signed little-endian PCM at 22050 Hz (Piper default)
        cmd_play = ["aplay", "-r", "22050", "-f", "S16_LE", "-t", "raw", "-"]

        try:
            self._proc = subprocess.Popen(
                cmd_piper,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
            )
            self._play_proc = subprocess.Popen(
                cmd_play,
                stdin=self._proc.stdout,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self._proc.stdout.close()  # allow _play_proc to receive EOF

            # Write text to piper stdin
            self._proc.stdin.write(sentence.encode("utf-8"))
            self._proc.stdin.close()

            # Estimate word timings while audio plays
            words = [w for w in re.split(r'\s+', sentence) if w]
            word_count = max(len(words), 1)
            # Average speaking rate: ~150 wpm at speed=1 → ms per word
            ms_per_word = (60_000 / 150) / self._speed

            start_time = time.monotonic()
            for w_idx, word in enumerate(words):
                if self._stop_event.is_set():
                    break
                self._pause_event.wait()
                elapsed = (time.monotonic() - start_time) * 1000
                self._emit_word(w_idx, elapsed)
                sleep_dur = ms_per_word / 1000
                # Sleep in small increments to react to stop/pause quickly
                deadline = time.monotonic() + sleep_dur
                while time.monotonic() < deadline:
                    if self._stop_event.is_set():
                        break
                    self._pause_event.wait()
                    time.sleep(0.02)

            if self._play_proc:
                self._play_proc.wait()
            if self._proc:
                self._proc.wait()

        except FileNotFoundError as exc:
            logger.error("Piper binary not found: %s", exc)
            self._set_state(TTSState.STOPPED)
        except Exception as exc:
            logger.error("PiperEngine error: %s", exc)

    def _apply_speed(self, speed: float) -> None:
        # Speed change takes effect on the next sentence.
        logger.debug("PiperEngine speed set to %.2f", speed)
