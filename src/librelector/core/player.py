"""Core Player: orchestrates EPUB parsing, TTS, and library state.

This is the main façade used by the UI layer.  It does NOT import any GTK
symbols; all UI updates are delivered via callback functions.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from ..epub import EpubBook, EpubChapter, EpubParser
from ..tts.base import TTSEngine, TTSState
from ..data.library import Library
from ..data.models import BookRecord, ReadingProgress
from .pronunciation import PronunciationDict

logger = logging.getLogger(__name__)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class Player:
    """High-level reading controller.

    Typical lifecycle
    -----------------
    1. ``player = Player(tts_engine, library)``
    2. ``player.open_book(path)``
    3. ``player.play()``
    4. ``player.pause()`` / ``player.resume()``
    5. ``player.next_chapter()`` / ``player.prev_chapter()``
    """

    def __init__(
        self,
        engine: TTSEngine,
        library: Library,
        pronunciation: Optional[PronunciationDict] = None,
    ) -> None:
        self._engine = engine
        self._library = library
        self._pronunciation = pronunciation or PronunciationDict()

        self._book: Optional[EpubBook] = None
        self._book_record: Optional[BookRecord] = None
        self._chapter_order: int = 0
        self._sentence_index: int = 0

        # UI callbacks (set by the window/widget)
        self._on_sentence_cb: Optional[Callable[[int], None]] = None
        self._on_word_cb: Optional[Callable[[int], None]] = None
        self._on_chapter_cb: Optional[Callable[[EpubChapter], None]] = None
        self._on_state_cb: Optional[Callable[[TTSState], None]] = None

        # Wire TTS → Player callbacks
        self._engine.set_on_sentence(self._handle_sentence)
        self._engine.set_on_word(self._handle_word)
        self._engine.set_on_finished(self._handle_chapter_finished)

    # ── public API ────────────────────────────────────────────────────────────

    def open_book(self, epub_path: str | Path) -> EpubBook:
        """Parse and load an EPUB; restore saved reading position."""
        epub_path = Path(epub_path)
        parser = EpubParser()
        self._book = parser.parse(epub_path)

        # Persist to library
        record = BookRecord(
            id=None,
            file_path=str(epub_path),
            title=self._book.title,
            author=self._book.author,
            language=self._book.language,
            identifier=self._book.identifier,
            cover_path=self._book.cover_path,
            chapter_count=self._book.chapter_count,
            added_at=_now_iso(),
        )
        self._book_record = self._library.add_book(record)

        # Restore progress
        progress = self._library.get_progress(self._book_record.id)
        if progress:
            self._chapter_order = progress.chapter_order
            self._sentence_index = progress.sentence_index
        else:
            self._chapter_order = 0
            self._sentence_index = 0

        logger.info("Book loaded: %s (chapters: %d)", self._book.title, self._book.chapter_count)
        return self._book

    def play(self) -> None:
        """Start or resume reading from the current position."""
        if self._book is None:
            raise RuntimeError("No book loaded. Call open_book() first.")

        if self._engine.state == TTSState.PAUSED:
            self._engine.resume()
            self._emit_state(TTSState.PLAYING)
            return

        self._speak_current_chapter()

    def pause(self) -> None:
        self._engine.pause()
        self._save_progress()
        self._emit_state(TTSState.PAUSED)

    def resume(self) -> None:
        self.play()

    def stop(self) -> None:
        self._engine.stop()
        self._save_progress()
        self._emit_state(TTSState.STOPPED)

    def next_chapter(self) -> bool:
        """Advance to the next chapter. Returns False if already at end."""
        if self._book is None:
            return False
        if self._chapter_order >= self._book.chapter_count - 1:
            return False
        self._engine.stop()
        self._chapter_order += 1
        self._sentence_index = 0
        chapter = self._current_chapter()
        self._emit_chapter(chapter)
        self._speak_current_chapter()
        return True

    def prev_chapter(self) -> bool:
        """Go back to the previous chapter. Returns False if at start."""
        if self._book is None or self._chapter_order <= 0:
            return False
        self._engine.stop()
        self._chapter_order -= 1
        self._sentence_index = 0
        chapter = self._current_chapter()
        self._emit_chapter(chapter)
        self._speak_current_chapter()
        return True

    def go_to_chapter(self, order: int) -> None:
        if self._book is None:
            return
        order = max(0, min(order, self._book.chapter_count - 1))
        self._engine.stop()
        self._chapter_order = order
        self._sentence_index = 0
        chapter = self._current_chapter()
        self._emit_chapter(chapter)
        self._speak_current_chapter()

    def set_speed(self, speed: float) -> None:
        self._engine.speed = speed

    def set_volume(self, volume: float) -> None:
        self._engine.volume = volume

    # ── callback registration ─────────────────────────────────────────────────

    def set_on_sentence(self, cb: Callable[[int], None]) -> None:
        """cb(sentence_index) – called when a new sentence starts."""
        self._on_sentence_cb = cb

    def set_on_word(self, cb: Callable[[int], None]) -> None:
        """cb(word_index) – called when a new word starts."""
        self._on_word_cb = cb

    def set_on_chapter(self, cb: Callable[[EpubChapter], None]) -> None:
        """cb(chapter) – called when the active chapter changes."""
        self._on_chapter_cb = cb

    def set_on_state(self, cb: Callable[[TTSState], None]) -> None:
        """cb(state) – called when playback state changes."""
        self._on_state_cb = cb

    # ── properties ────────────────────────────────────────────────────────────

    @property
    def book(self) -> Optional[EpubBook]:
        return self._book

    @property
    def current_chapter(self) -> Optional[EpubChapter]:
        return self._current_chapter()

    @property
    def current_sentence_index(self) -> int:
        return self._sentence_index

    @property
    def state(self) -> TTSState:
        return self._engine.state

    # ── private ───────────────────────────────────────────────────────────────

    def _current_chapter(self) -> Optional[EpubChapter]:
        if self._book is None:
            return None
        return self._book.chapter_by_order(self._chapter_order)

    def _speak_current_chapter(self) -> None:
        chapter = self._current_chapter()
        if chapter is None:
            return
        self._emit_chapter(chapter)

        text = self._pronunciation.apply(chapter.plain_text)
        self._engine.speak(text, start_sentence=self._sentence_index)
        self._emit_state(TTSState.PLAYING)

    def _handle_sentence(self, idx: int, _ms: float) -> None:
        self._sentence_index = idx
        if self._on_sentence_cb:
            self._on_sentence_cb(idx)

    def _handle_word(self, idx: int, _ms: float) -> None:
        if self._on_word_cb:
            self._on_word_cb(idx)

    def _handle_chapter_finished(self) -> None:
        """Called by TTS engine when a chapter's audio ends → auto-advance."""
        advanced = self.next_chapter()
        if not advanced:
            logger.info("End of book reached.")
            self._emit_state(TTSState.IDLE)

    def _save_progress(self) -> None:
        if self._book_record is None or self._book_record.id is None:
            return
        self._library.save_progress(
            ReadingProgress(
                book_id=self._book_record.id,
                chapter_order=self._chapter_order,
                sentence_index=self._sentence_index,
                char_offset=0,
                audio_ms=0.0,
                updated_at=_now_iso(),
            )
        )

    def _emit_chapter(self, chapter: Optional[EpubChapter]) -> None:
        if chapter and self._on_chapter_cb:
            self._on_chapter_cb(chapter)

    def _emit_state(self, state: TTSState) -> None:
        if self._on_state_cb:
            self._on_state_cb(state)
