"""Sidebar: library list of EPUB books."""
from __future__ import annotations

import logging
from pathlib import Path

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, GdkPixbuf, GLib, GObject, Gtk  # noqa: E402

from ..data.library import Library

logger = logging.getLogger(__name__)


class LibraryView(Gtk.Box):
    """Vertical box showing the user's book collection."""

    __gsignals__ = {
        "book-selected": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "book-add-requested": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, library: Library) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._library = library
        self._build()
        self.refresh()

    # ── build ─────────────────────────────────────────────────────────────────

    def _build(self) -> None:
        # Header bar for the sidebar
        header = Adw.HeaderBar()
        header.set_show_end_title_buttons(False)

        add_btn = Gtk.Button(icon_name="list-add-symbolic", tooltip_text="Ajouter un livre")
        add_btn.connect("clicked", lambda _: self.emit("book-add-requested"))
        header.pack_end(add_btn)

        title_widget = Adw.WindowTitle(title="Bibliothèque")
        header.set_title_widget(title_widget)

        self.append(header)

        # Scrollable list
        scroll = Gtk.ScrolledWindow(vexpand=True)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self._list_box = Gtk.ListBox(selection_mode=Gtk.SelectionMode.SINGLE)
        self._list_box.set_css_classes(["navigation-sidebar"])
        self._list_box.connect("row-activated", self._on_row_activated)
        scroll.set_child(self._list_box)
        self.append(scroll)

    # ── public ────────────────────────────────────────────────────────────────

    def refresh(self) -> None:
        """Reload the book list from the library database."""
        # Remove existing rows
        while (row := self._list_box.get_first_child()) is not None:
            self._list_box.remove(row)

        books = self._library.all_books()
        if not books:
            placeholder = Adw.StatusPage(
                title="Aucun livre",
                description="Cliquez + pour ajouter un fichier EPUB",
                icon_name="book-open-variant-symbolic",
            )
            placeholder.set_vexpand(True)
            row = Gtk.ListBoxRow(child=placeholder, activatable=False, selectable=False)
            self._list_box.append(row)
            return

        for book in books:
            row = self._make_row(book)
            self._list_box.append(row)

    # ── private ───────────────────────────────────────────────────────────────

    def _make_row(self, book) -> Gtk.ListBoxRow:
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12, margin_top=6, margin_bottom=6,
                      margin_start=12, margin_end=12)

        # Cover thumbnail
        cover_img = Gtk.Image(pixel_size=48)
        if book.cover_path and Path(book.cover_path).exists():
            try:
                pb = GdkPixbuf.Pixbuf.new_from_file_at_scale(book.cover_path, 48, 64, True)
                cover_img.set_from_pixbuf(pb)
            except Exception:
                cover_img.set_from_icon_name("book-open-variant-symbolic")
        else:
            cover_img.set_from_icon_name("book-open-variant-symbolic")
        box.append(cover_img)

        # Text info
        text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2, valign=Gtk.Align.CENTER)
        title_lbl = Gtk.Label(
            label=book.title,
            halign=Gtk.Align.START,
            ellipsize=Pango.EllipsizeMode.END,
            max_width_chars=24,
            css_classes=["body"],
        )
        author_lbl = Gtk.Label(
            label=book.author,
            halign=Gtk.Align.START,
            ellipsize=Pango.EllipsizeMode.END,
            max_width_chars=24,
            css_classes=["caption", "dim-label"],
        )
        text_box.append(title_lbl)
        text_box.append(author_lbl)
        box.append(text_box)

        row = Gtk.ListBoxRow(child=box)
        row._book_path = book.file_path  # store for signal handler
        return row

    def _on_row_activated(self, _list_box, row: Gtk.ListBoxRow) -> None:
        path = getattr(row, "_book_path", None)
        if path:
            self.emit("book-selected", path)


# Need Pango for ellipsize
from gi.repository import Pango  # noqa: E402, F401 (imported for use above)
