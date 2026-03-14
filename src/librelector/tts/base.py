"""Abstract base class for TTS engines."""
from __future__ import annotations

import threading
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Callable, Optional


class TTSState(Enum):
    IDLE = auto()
    PLAYING = auto()
    PAUSED = auto()
    STOPPED = auto()


# Callback type: called with (segment_index, audio_position_ms)
ProgressCallback = Callable[[int, float], None]


class TTSEngine(ABC):
    """
    Abstract TTS engine.

    Subclasses implement synthesis and playback.  The engine runs audio in a
    background thread; the UI receives progress via *on_word* / *on_sentence*
    callbacks.
    """

    def __init__(self) -> None:
        self._state = TTSState.IDLE
        self._state_lock = threading.Lock()
        self._speed: float = 1.0          # 0.5 – 2.0
        self._volume: float = 1.0         # 0.0 – 1.0
        self._on_sentence: Optional[ProgressCallback] = None
        self._on_word: Optional[ProgressCallback] = None
        self._on_finished: Optional[Callable[[], None]] = None

    # ── properties ────────────────────────────────────────────────────────────

    @property
    def state(self) -> TTSState:
        with self._state_lock:
            return self._state

    @property
    def speed(self) -> float:
        return self._speed

    @speed.setter
    def speed(self, value: float) -> None:
        self._speed = max(0.25, min(4.0, value))
        self._apply_speed(self._speed)

    @property
    def volume(self) -> float:
        return self._volume

    @volume.setter
    def volume(self, value: float) -> None:
        self._volume = max(0.0, min(1.0, value))
        self._apply_volume(self._volume)

    # ── callbacks ─────────────────────────────────────────────────────────────

    def set_on_sentence(self, cb: ProgressCallback) -> None:
        """Called when a new sentence starts: cb(sentence_index, ms)."""
        self._on_sentence = cb

    def set_on_word(self, cb: ProgressCallback) -> None:
        """Called when a new word starts: cb(word_index, ms)."""
        self._on_word = cb

    def set_on_finished(self, cb: Callable[[], None]) -> None:
        """Called when playback of the current text finishes."""
        self._on_finished = cb

    # ── abstract interface ────────────────────────────────────────────────────

    @abstractmethod
    def speak(self, text: str, start_sentence: int = 0) -> None:
        """
        Start speaking *text*.

        Parameters
        ----------
        text:
            Plain text to synthesise.
        start_sentence:
            Sentence index to begin from (for resume functionality).
        """

    @abstractmethod
    def stop(self) -> None:
        """Stop playback immediately."""

    @abstractmethod
    def pause(self) -> None:
        """Pause playback."""

    @abstractmethod
    def resume(self) -> None:
        """Resume paused playback."""

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if the engine dependencies are installed and ready."""

    # ── optional overrides ────────────────────────────────────────────────────

    def _apply_speed(self, speed: float) -> None:  # noqa: B027
        """Apply speed change to a running engine (override if supported)."""

    def _apply_volume(self, volume: float) -> None:  # noqa: B027
        """Apply volume change to a running engine (override if supported)."""

    # ── helpers ───────────────────────────────────────────────────────────────

    def _set_state(self, state: TTSState) -> None:
        with self._state_lock:
            self._state = state

    def _emit_sentence(self, idx: int, ms: float = 0.0) -> None:
        if self._on_sentence:
            self._on_sentence(idx, ms)

    def _emit_word(self, idx: int, ms: float = 0.0) -> None:
        if self._on_word:
            self._on_word(idx, ms)

    def _emit_finished(self) -> None:
        if self._on_finished:
            self._on_finished()
