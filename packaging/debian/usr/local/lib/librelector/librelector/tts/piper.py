"""Piper TTS engine – offline neural voices.

Piper (https://github.com/rhasspy/piper) is a fast, local neural TTS engine.
It is invoked as a subprocess:  echo "text" | piper --model voice.onnx --output_raw | aplay

A single Piper process handles the whole chapter (one sentence per stdin line)
to avoid the model-reload overhead (~5 s) between sentences.
"""
from __future__ import annotations

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
        self._pause_event.set()
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
        """Background thread: send all sentences to a single Piper process."""
        from ..epub.parser import _split_sentences

        sentences = _split_sentences(text)
        if start_sentence:
            sentences = sentences[start_sentence:]
        if not sentences:
            return

        cmd_piper = [
            self._piper_bin(),
            "--model", str(self.model_path),
            "--output_raw",
            "--length_scale", f"{1.0 / self._speed:.2f}",
        ]
        if self.config_path.exists():
            cmd_piper += ["--config", str(self.config_path)]

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
            self._proc.stdout.close()

            # Send all sentences at once — Piper reads one line at a time
            for sentence in sentences:
                self._proc.stdin.write((sentence.strip() + "\n").encode("utf-8"))
            self._proc.stdin.close()

            # Emit sentence/word events based on estimated timing (~150 wpm)
            ms_per_word = (60_000 / 150) / self._speed
            for idx, sentence in enumerate(sentences):
                if self._stop_event.is_set():
                    break
                self._pause_event.wait()
                if self._stop_event.is_set():
                    break

                self._emit_sentence(idx + start_sentence)

                words = [w for w in re.split(r'\s+', sentence) if w]
                for w_idx, _ in enumerate(words):
                    if self._stop_event.is_set():
                        break
                    self._pause_event.wait()
                    self._emit_word(w_idx, w_idx * ms_per_word)
                    deadline = time.monotonic() + ms_per_word / 1000
                    while time.monotonic() < deadline:
                        if self._stop_event.is_set():
                            break
                        time.sleep(0.02)

            if not self._stop_event.is_set():
                self._play_proc.wait()
                self._proc.wait()
            else:
                self._kill_procs()

        except FileNotFoundError as exc:
            logger.error("Piper binary not found: %s", exc)
            self._set_state(TTSState.STOPPED)
            return
        except Exception as exc:
            logger.error("PiperEngine error: %s", exc)
            return

        if not self._stop_event.is_set():
            self._set_state(TTSState.IDLE)
            self._emit_finished()

    def _apply_speed(self, speed: float) -> None:
        logger.debug("PiperEngine speed set to %.2f", speed)
