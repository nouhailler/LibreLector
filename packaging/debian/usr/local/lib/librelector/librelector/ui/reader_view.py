"""Reader view: text display + playback controls + chapter navigation."""
from __future__ import annotations

import logging
from typing import Optional

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio, GLib, GObject, Gtk, Pango  # noqa: E402

from ..epub.models import EpubBook, EpubChapter
from ..tts.base import TTSState

logger = logging.getLogger(__name__)

# Try to import WebKit for rich HTML rendering; fall back to Gtk.TextView
try:
    gi.require_version("WebKit", "6.0")
    from gi.repository import WebKit  # noqa: F401
    _WEBKIT_AVAILABLE = True
except Exception:
    _WEBKIT_AVAILABLE = False
    logger.info("WebKitGTK not available – using plain text fallback")


class ReaderView(Gtk.Box):
    """Content area: TOC sidebar + text panel + player controls."""

    __gsignals__ = {
        "play-pause":      (GObject.SignalFlags.RUN_FIRST, None, ()),
        "stop":            (GObject.SignalFlags.RUN_FIRST, None, ()),
        "next-chapter":    (GObject.SignalFlags.RUN_FIRST, None, ()),
        "prev-chapter":    (GObject.SignalFlags.RUN_FIRST, None, ()),
        "speed-changed":   (GObject.SignalFlags.RUN_FIRST, None, (float,)),
        "volume-changed":  (GObject.SignalFlags.RUN_FIRST, None, (float,)),
        "chapter-selected":(GObject.SignalFlags.RUN_FIRST, None, (int,)),
        "export-requested": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "open-requested":   (GObject.SignalFlags.RUN_FIRST, None, ()),
        "quit-requested":   (GObject.SignalFlags.RUN_FIRST, None, ()),
        "sentence-selected": (GObject.SignalFlags.RUN_FIRST, None, (int,)),
    }

    def __init__(self) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._book: Optional[EpubBook] = None
        self._chapter: Optional[EpubChapter] = None
        self._current_sentence: int = 0
        self._current_word: int = 0
        self._build()

    # ── build ─────────────────────────────────────────────────────────────────

    def _build(self) -> None:
        # ── Header bar ────────────────────────────────────────────────────────
        self._header = Adw.HeaderBar()
        # Menu hamburger
        menu = Gio.Menu()
        menu.append("Ouvrir un EPUB…", "win.open")
        menu.append("Exporter en MP3…", "win.export")
        menu.append("Quitter", "win.quit")
        btn_menu = Gtk.MenuButton(icon_name="open-menu-symbolic",
                                  menu_model=menu,
                                  primary=True)
        self._header.pack_end(btn_menu)
        self._title_widget = Adw.WindowTitle(title="LibreLector", subtitle="")
        self._header.set_title_widget(self._title_widget)
        self.append(self._header)

        # ── Inner box (paned + controls) wrapped in ToastOverlay ──────────────
        inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, vexpand=True)

        # ── Main body: TOC pane + text area ───────────────────────────────────
        self._paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL, vexpand=True)

        # TOC panel (left)
        toc_scroll = Gtk.ScrolledWindow(width_request=200)
        toc_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self._toc_list = Gtk.ListBox(selection_mode=Gtk.SelectionMode.SINGLE,
                                     css_classes=["navigation-sidebar"])
        self._toc_list.connect("row-activated", self._on_toc_row_activated)
        toc_scroll.set_child(self._toc_list)
        self._paned.set_start_child(toc_scroll)
        self._paned.set_shrink_start_child(False)

        # Text area (right)
        self._text_scroll = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        self._text_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self._text_view = self._make_text_view()
        gesture = Gtk.GestureClick.new()
        gesture.connect("pressed", self._on_text_clicked)
        self._text_view.add_controller(gesture)
        self._text_scroll.set_child(self._text_view)
        self._paned.set_end_child(self._text_scroll)
        self._paned.set_position(220)

        inner.append(self._paned)
        inner.append(self._build_controls())

        self._toast_overlay = Adw.ToastOverlay()
        self._toast_overlay.set_child(inner)
        self.append(self._toast_overlay)

    def _make_text_view(self) -> Gtk.TextView:
        tv = Gtk.TextView(editable=False, cursor_visible=False, wrap_mode=Gtk.WrapMode.WORD_CHAR,
                          left_margin=24, right_margin=24, top_margin=16, bottom_margin=16,
                          pixels_above_lines=4)
        tv.set_monospace(False)
        # Text tags for highlighting
        buf = tv.get_buffer()
        buf.create_tag("sentence-highlight", background="#FFD700", foreground="#000000")
        buf.create_tag("word-highlight",     background="#FF8C00", foreground="#FFFFFF",
                       weight=Pango.Weight.BOLD)
        buf.create_tag("normal", background=None, foreground=None)
        return tv

    def _build_controls(self) -> Gtk.Box:
        bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8,
                      margin_top=8, margin_bottom=12, margin_start=16, margin_end=16,
                      halign=Gtk.Align.CENTER)

        # Prev chapter
        self._btn_prev = Gtk.Button(icon_name="media-skip-backward-symbolic",
                                    tooltip_text="Chapitre précédent")
        self._btn_prev.connect("clicked", lambda _: self.emit("prev-chapter"))

        # Play / Pause
        self._btn_play = Gtk.Button(icon_name="media-playback-start-symbolic",
                                    tooltip_text="Lecture / Pause",
                                    css_classes=["suggested-action", "circular"])
        self._btn_play.connect("clicked", lambda _: self.emit("play-pause"))

        # Stop
        self._btn_stop = Gtk.Button(icon_name="media-playback-stop-symbolic",
                                    tooltip_text="Arrêter")
        self._btn_stop.connect("clicked", lambda _: self.emit("stop"))

        # Next chapter
        self._btn_next = Gtk.Button(icon_name="media-skip-forward-symbolic",
                                    tooltip_text="Chapitre suivant")
        self._btn_next.connect("clicked", lambda _: self.emit("next-chapter"))

        # Speed
        speed_lbl = Gtk.Label(label="Vitesse :")
        self._speed_spin = Gtk.SpinButton(
            adjustment=Gtk.Adjustment(value=1.0, lower=0.25, upper=4.0,
                                      step_increment=0.25, page_increment=0.5),
            digits=2,
        )
        self._speed_spin.connect("value-changed", self._on_speed_changed)

        # Volume
        vol_icon = Gtk.Image(icon_name="audio-volume-high-symbolic")
        self._vol_scale = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL,
            adjustment=Gtk.Adjustment(value=1.0, lower=0.0, upper=1.0,
                                      step_increment=0.05, page_increment=0.1),
            width_request=120,
            draw_value=False,
        )
        self._vol_scale.connect("value-changed", self._on_volume_changed)

        for widget in (
            self._btn_prev, self._btn_play, self._btn_stop, self._btn_next,
            Gtk.Separator(orientation=Gtk.Orientation.VERTICAL, margin_start=8, margin_end=8),
            speed_lbl, self._speed_spin,
            Gtk.Separator(orientation=Gtk.Orientation.VERTICAL, margin_start=8, margin_end=8),
            vol_icon, self._vol_scale,
        ):
            bar.append(widget)

        return bar

    # ── public API ────────────────────────────────────────────────────────────

    def show_toast(self, message: str, timeout: int = 4) -> None:
        toast = Adw.Toast(title=message, timeout=timeout)
        self._toast_overlay.add_toast(toast)

    def load_book(self, book: EpubBook) -> None:
        self._book = book
        self._title_widget.set_title(book.title)
        self._title_widget.set_subtitle(book.author)
        self._populate_toc(book)

    def display_chapter(self, chapter: EpubChapter, sentence_idx: int = 0) -> None:
        self._chapter = chapter
        self._current_sentence = sentence_idx
        self._current_word = 0

        buf = self._text_view.get_buffer()
        buf.set_text(chapter.plain_text)
        # Scroll to top
        buf.place_cursor(buf.get_start_iter())
        self._text_view.scroll_to_iter(buf.get_start_iter(), 0.0, False, 0, 0)

        if sentence_idx > 0:
            self.highlight_sentence(sentence_idx)

        self.select_toc_chapter(chapter.order)

    def highlight_sentence(self, idx: int) -> None:
        """Highlight sentence *idx* in the text view."""
        self._current_sentence = idx
        if self._chapter is None or idx >= len(self._chapter.sentences):
            return
        seg = self._chapter.sentences[idx]
        buf = self._text_view.get_buffer()

        # Remove previous highlights
        buf.remove_tag_by_name("sentence-highlight", buf.get_start_iter(), buf.get_end_iter())
        buf.remove_tag_by_name("word-highlight",     buf.get_start_iter(), buf.get_end_iter())

        start = buf.get_iter_at_offset(seg.char_start)
        end   = buf.get_iter_at_offset(seg.char_end)
        buf.apply_tag_by_name("sentence-highlight", start, end)

        # Scroll the highlighted sentence into view
        self._text_view.scroll_to_iter(start, 0.1, False, 0, 0)

    def highlight_word(self, idx: int) -> None:
        """Highlight word *idx* (within current sentence context)."""
        self._current_word = idx
        if self._chapter is None or idx >= len(self._chapter.words):
            return
        seg = self._chapter.words[idx]
        buf = self._text_view.get_buffer()

        # Keep sentence highlight; replace word highlight only
        buf.remove_tag_by_name("word-highlight", buf.get_start_iter(), buf.get_end_iter())
        start = buf.get_iter_at_offset(seg.char_start)
        end   = buf.get_iter_at_offset(seg.char_end)
        buf.apply_tag_by_name("word-highlight", start, end)

    def update_state(self, state: TTSState) -> None:
        if state == TTSState.PLAYING:
            self._btn_play.set_icon_name("media-playback-pause-symbolic")
            self._btn_play.set_tooltip_text("Pause")
        else:
            self._btn_play.set_icon_name("media-playback-start-symbolic")
            self._btn_play.set_tooltip_text("Lecture")

    # ── private ───────────────────────────────────────────────────────────────

    def _populate_toc(self, book: EpubBook) -> None:
        while (child := self._toc_list.get_first_child()) is not None:
            self._toc_list.remove(child)

        for chapter in book.chapters:
            lbl = Gtk.Label(
                label=chapter.title,
                halign=Gtk.Align.START,
                ellipsize=Pango.EllipsizeMode.END,
                max_width_chars=22,
                margin_top=6, margin_bottom=6, margin_start=12, margin_end=8,
            )
            row = Gtk.ListBoxRow(child=lbl)
            row._chapter_order = chapter.order
            self._toc_list.append(row)

    def select_toc_chapter(self, order: int) -> None:
        """Highlight the active chapter row in the TOC."""
        row = self._toc_list.get_row_at_index(order)
        if row:
            self._toc_list.select_row(row)
            # Scroll the TOC to make the active row visible
            adj = self._toc_list.get_parent().get_vadjustment()
            if adj:
                alloc = row.get_allocation()
                adj.set_value(max(0, alloc.y - 50))

    def _on_toc_row_activated(self, _list_box, row: Gtk.ListBoxRow) -> None:
        order = getattr(row, "_chapter_order", 0)
        self.emit("chapter-selected", order)

    def _on_text_clicked(self, gesture, n_press, x, y) -> None:
        if self._chapter is None or n_press != 2:  # double-clic
            return
        bx, by = self._text_view.window_to_buffer_coords(
            Gtk.TextWindowType.WIDGET, int(x), int(y))
        ok, it = self._text_view.get_iter_at_location(bx, by)
        if not ok:
            return
        offset = it.get_offset()
        for seg in self._chapter.sentences:
            if seg.char_start <= offset <= seg.char_end:
                self.emit("sentence-selected", seg.index)
                return

    def _on_speed_changed(self, spin: Gtk.SpinButton) -> None:
        self.emit("speed-changed", spin.get_value())

    def _on_volume_changed(self, scale: Gtk.Scale) -> None:
        self.emit("volume-changed", scale.get_value())
