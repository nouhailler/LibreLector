"""Main application window."""
from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Optional

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, GLib, Gtk, Pango  # noqa: E402

from ..core.player import Player
from ..data.library import Library
from ..tts.base import TTSState
from ..epub.models import EpubChapter
from .library_view import LibraryView
from .reader_view import ReaderView
from .settings_dialog import SettingsDialog

logger = logging.getLogger(__name__)


class MainWindow(Adw.ApplicationWindow):
    """LibreLector main window.

    Layout (Adw.NavigationSplitView):
    ┌──────────────────────────────────────────────┐
    │  HeaderBar                                   │
    ├──────────────┬───────────────────────────────┤
    │ LibraryView  │ ReaderView                    │
    │ (sidebar)    │ (content + player controls)   │
    └──────────────┴───────────────────────────────┘
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(
            title="LibreLector",
            default_width=1100,
            default_height=720,
            **kwargs,
        )

        # ── data / logic ──────────────────────────────────────────────────────
        self._library = Library()
        self._player: Optional[Player] = None
        self._settings = self._load_settings()

        # ── build UI ──────────────────────────────────────────────────────────
        self._build_ui()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        # Top-level layout: navigation split (sidebar | content)
        self._split = Adw.NavigationSplitView()

        # Sidebar – library
        self._library_view = LibraryView(self._library)
        self._library_view.connect("book-selected", self._on_book_selected)
        self._library_view.connect("book-add-requested", self._on_add_book)

        sidebar_page = Adw.NavigationPage(
            title="Bibliothèque",
            child=self._library_view,
        )

        # Content – reader
        self._reader_view = ReaderView()
        self._reader_view.connect("play-pause", self._on_play_pause)
        self._reader_view.connect("stop", self._on_stop)
        self._reader_view.connect("next-chapter", self._on_next_chapter)
        self._reader_view.connect("prev-chapter", self._on_prev_chapter)
        self._reader_view.connect("speed-changed", self._on_speed_changed)
        self._reader_view.connect("volume-changed", self._on_volume_changed)
        self._reader_view.connect("chapter-selected", self._on_chapter_jump)

        content_page = Adw.NavigationPage(
            title="LibreLector",
            child=self._reader_view,
        )

        self._split.set_sidebar(sidebar_page)
        self._split.set_content(content_page)

        self.set_content(self._split)

    # ── file opening ──────────────────────────────────────────────────────────

    def open_file(self, path: str) -> None:
        """Open an EPUB from a file path (called from CLI or file chooser)."""
        def _open():
            try:
                player = self._get_or_create_player()
                book = player.open_book(path)
                GLib.idle_add(self._on_book_loaded, book)
            except Exception as exc:
                logger.error("Failed to open book: %s", exc)
                GLib.idle_add(self._show_error, str(exc))

        threading.Thread(target=_open, daemon=True, name="OpenBook").start()

    def _on_book_loaded(self, book) -> None:
        self._reader_view.load_book(book)
        chapter = self._player.current_chapter
        if chapter:
            self._reader_view.display_chapter(chapter, sentence_idx=self._player.current_sentence_index)
        return False  # GLib.idle_add

    # ── player interaction ────────────────────────────────────────────────────

    def _on_book_selected(self, _widget, path: str) -> None:
        self.open_file(path)

    def _on_add_book(self, _widget) -> None:
        dialog = Gtk.FileDialog(
            title="Ouvrir un fichier EPUB",
            modal=True,
        )
        f = Gtk.FileFilter()
        f.set_name("Fichiers EPUB")
        f.add_pattern("*.epub")
        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(f)
        dialog.set_filters(filters)
        dialog.open(self, None, self._on_file_chosen)

    def _on_file_chosen(self, dialog: Gtk.FileDialog, result) -> None:
        try:
            file = dialog.open_finish(result)
            if file:
                self.open_file(file.get_path())
                self._library_view.refresh()
        except Exception as exc:
            logger.error("File chooser error: %s", exc)

    def _on_play_pause(self, _widget) -> None:
        if self._player is None:
            return
        state = self._player.state
        if state == TTSState.PLAYING:
            self._player.pause()
        else:
            self._player.play()

    def _on_stop(self, _widget) -> None:
        if self._player:
            self._player.stop()

    def _on_next_chapter(self, _widget) -> None:
        if self._player:
            self._player.next_chapter()

    def _on_prev_chapter(self, _widget) -> None:
        if self._player:
            self._player.prev_chapter()

    def _on_speed_changed(self, _widget, speed: float) -> None:
        if self._player:
            self._player.set_speed(speed)

    def _on_volume_changed(self, _widget, volume: float) -> None:
        if self._player:
            self._player.set_volume(volume)

    def _on_chapter_jump(self, _widget, order: int) -> None:
        if self._player:
            self._player.go_to_chapter(order)

    # ── player callbacks (from background thread → GTK main loop) ─────────────

    def _handle_sentence(self, idx: int) -> None:
        GLib.idle_add(self._reader_view.highlight_sentence, idx)

    def _handle_word(self, idx: int) -> None:
        GLib.idle_add(self._reader_view.highlight_word, idx)

    def _handle_chapter(self, chapter: EpubChapter) -> None:
        GLib.idle_add(self._reader_view.display_chapter, chapter, 0)

    def _handle_state(self, state: TTSState) -> None:
        GLib.idle_add(self._reader_view.update_state, state)

    # ── helpers ───────────────────────────────────────────────────────────────

    def _get_or_create_player(self) -> Player:
        if self._player is None:
            from ..tts.factory import create_engine
            engine = create_engine(
                preferred=self._settings.get("tts_engine", "speech_dispatcher"),
                piper_model=self._settings.get("piper_model"),
                language=self._settings.get("language", "fr"),
            )
            self._player = Player(engine, self._library)
            self._player.set_on_sentence(self._handle_sentence)
            self._player.set_on_word(self._handle_word)
            self._player.set_on_chapter(self._handle_chapter)
            self._player.set_on_state(self._handle_state)
        return self._player

    def _load_settings(self) -> dict:
        import json
        settings_path = Path.home() / ".local" / "share" / "LibreLector" / "settings.json"
        if settings_path.exists():
            try:
                return json.loads(settings_path.read_text())
            except Exception:
                pass
        return {}

    def _show_error(self, message: str) -> None:
        dialog = Adw.MessageDialog(
            transient_for=self,
            heading="Erreur",
            body=message,
        )
        dialog.add_response("ok", "OK")
        dialog.present()
        return False
