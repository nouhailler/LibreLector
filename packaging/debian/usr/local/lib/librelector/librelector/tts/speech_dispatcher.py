"""Speech Dispatcher TTS engine – system-wide TTS fallback.

Speech Dispatcher (spd-say / libspeechd) is available on most Linux desktops.
It supports many backends (espeak-ng, festival, etc.).
"""
from __future__ import annotations

import logging
import shutil
import subprocess
import threading
import re
import time
from typing import Optional

from .base import TTSEngine, TTSState

logger = logging.getLogger(__name__)


class SpeechDispatcherEngine(TTSEngine):
    """TTS engine backed by ``spd-say`` (Speech Dispatcher)."""

    def __init__(self, voice: Optional[str] = None, language: str = "fr"):
        super().__init__()
        self._voice = voice
        self._language = language
        self._proc: Optional[subprocess.Popen] = None
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._pause_event.set()

    def is_available(self) -> bool:
        return bool(shutil.which("spd-say"))

    def speak(self, text: str, start_sentence: int = 0) -> None:
        self.stop()
        self._stop_event.clear()
        self._pause_event.set()
        self._set_state(TTSState.PLAYING)
        self._thread = threading.Thread(
            target=self._run,
            args=(text, start_sentence),
            daemon=True,
            name="SpdEngine-speak",
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        self._pause_event.set()
        if self._proc and self._proc.poll() is None:
            try:
                self._proc.terminate()
                self._proc.wait(timeout=1)
            except Exception:
                pass
        if self._thread and self._thread.is_alive() and self._thread != threading.current_thread():
            self._thread.join(timeout=2)
        self._set_state(TTSState.STOPPED)

    def pause(self) -> None:
        if self.state == TTSState.PLAYING:
            self._pause_event.clear()
            if self._proc and self._proc.poll() is None:
                self._proc.terminate()
            self._set_state(TTSState.PAUSED)

    def resume(self) -> None:
        if self.state == TTSState.PAUSED:
            self._set_state(TTSState.PLAYING)
            self._pause_event.set()

    # ── internal ─────────────────────────────────────────────────────────────

    def _run(self, text: str, start_sentence: int) -> None:
        from ..epub.parser import _split_sentences

        sentences = _split_sentences(text)
        if start_sentence:
            sentences = sentences[start_sentence:]

        for idx, sentence in enumerate(sentences):
            if self._stop_event.is_set():
                break
            self._pause_event.wait()
            if self._stop_event.is_set():
                break

            global_idx = idx + start_sentence
            self._emit_sentence(global_idx)

            cmd = ["spd-say", "-w"]   # -w → wait until done
            if self._language:
                cmd += ["-l", self._language]
            if self._voice:
                cmd += ["-t", self._voice]
            # Speed: spd-say accepts -r <rate> -100..100
            rate = int((self._speed - 1.0) * 100)
            cmd += ["-r", str(max(-100, min(100, rate)))]
            cmd.append(sentence)

            try:
                self._proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                # Emit approximate word events while spd-say runs
                words = [w for w in re.split(r'\s+', sentence) if w]
                ms_per_word = (60_000 / 150) / self._speed
                t0 = time.monotonic()
                for w_idx, _ in enumerate(words):
                    if self._stop_event.is_set():
                        break
                    self._pause_event.wait()
                    elapsed = (time.monotonic() - t0) * 1000
                    self._emit_word(w_idx, elapsed)
                    deadline = time.monotonic() + ms_per_word / 1000
                    while time.monotonic() < deadline:
                        if self._stop_event.is_set() or self._proc.poll() is not None:
                            break
                        time.sleep(0.02)

                self._proc.wait()
            except Exception as exc:
                logger.error("SpeechDispatcherEngine error: %s", exc)

        if not self._stop_event.is_set():
            self._set_state(TTSState.IDLE)
            self._emit_finished()
