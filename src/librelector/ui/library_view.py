"""Sidebar: library list of EPUB books with folder support."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, GdkPixbuf, GObject, Gtk, Pango  # noqa: E402

from ..data.library import Library
from ..data.models import BookRecord, Folder

logger = logging.getLogger(__name__)

_COVER_SIZE = 40


class LibraryView(Gtk.Box):
    """Sidebar affichant la bibliothèque organisée en dossiers."""

    __gsignals__ = {
        "book-selected":      (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "book-add-requested": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, library: Library) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._library = library
        self._build()
        self.refresh()

    # ── construction ──────────────────────────────────────────────────────────

    def _build(self) -> None:
        header = Adw.HeaderBar()
        header.set_show_end_title_buttons(False)
        header.set_title_widget(Adw.WindowTitle(title="Bibliothèque"))

        add_book_btn = Gtk.Button(
            icon_name="list-add-symbolic",
            tooltip_text="Ajouter un livre",
        )
        add_book_btn.connect("clicked", lambda _: self.emit("book-add-requested"))
        header.pack_end(add_book_btn)

        new_folder_btn = Gtk.Button(
            icon_name="folder-new-symbolic",
            tooltip_text="Nouveau dossier",
        )
        new_folder_btn.connect("clicked", self._on_new_folder)
        header.pack_end(new_folder_btn)

        self.append(header)

        scroll = Gtk.ScrolledWindow(vexpand=True)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self._list_box = Gtk.ListBox(selection_mode=Gtk.SelectionMode.NONE)
        self._list_box.set_css_classes(["navigation-sidebar"])
        scroll.set_child(self._list_box)
        self.append(scroll)

    # ── public ────────────────────────────────────────────────────────────────

    def refresh(self) -> None:
        while (child := self._list_box.get_first_child()) is not None:
            self._list_box.remove(child)

        books = self._library.all_books()
        folders = self._library.all_folders()

        if not books:
            self._show_placeholder()
            return

        if not folders:
            # Liste plate (comportement original si aucun dossier n'existe)
            for book in books:
                self._list_box.append(self._make_book_row(book))
            return

        # Regrouper les livres par dossier
        by_folder: dict[Optional[int], list[BookRecord]] = {}
        for book in books:
            by_folder.setdefault(book.folder_id, []).append(book)

        for folder in folders:
            expander = self._make_folder_expander(folder, by_folder.get(folder.id, []))
            self._list_box.append(expander)

        orphans = by_folder.get(None, [])
        if orphans:
            self._list_box.append(self._make_orphan_expander(orphans))

    # ── widgets ───────────────────────────────────────────────────────────────

    def _show_placeholder(self) -> None:
        placeholder = Adw.StatusPage(
            title="Aucun livre",
            description="Cliquez + pour ajouter un fichier EPUB",
            icon_name="book-open-variant-symbolic",
        )
        placeholder.set_vexpand(True)
        self._list_box.append(
            Gtk.ListBoxRow(child=placeholder, activatable=False, selectable=False)
        )

    def _make_folder_expander(self, folder: Folder, books: list[BookRecord]) -> Adw.ExpanderRow:
        n = len(books)
        expander = Adw.ExpanderRow()
        expander.set_title(folder.name)
        expander.set_subtitle(f"{n} livre{'s' if n != 1 else ''}")
        expander.set_icon_name("folder-symbolic")
        expander.set_expanded(True)

        rename_btn = Gtk.Button(
            icon_name="document-edit-symbolic",
            tooltip_text="Renommer",
            valign=Gtk.Align.CENTER,
            css_classes=["flat"],
        )
        rename_btn.connect("clicked", self._on_rename_folder, folder)
        expander.add_suffix(rename_btn)

        delete_btn = Gtk.Button(
            icon_name="user-trash-symbolic",
            tooltip_text="Supprimer le dossier",
            valign=Gtk.Align.CENTER,
            css_classes=["flat"],
        )
        delete_btn.connect("clicked", self._on_delete_folder, folder)
        expander.add_suffix(delete_btn)

        for book in books:
            expander.add_row(self._make_book_row(book))

        return expander

    def _make_orphan_expander(self, books: list[BookRecord]) -> Adw.ExpanderRow:
        n = len(books)
        expander = Adw.ExpanderRow()
        expander.set_title("Sans dossier")
        expander.set_subtitle(f"{n} livre{'s' if n != 1 else ''}")
        expander.set_icon_name("folder-open-symbolic")
        expander.set_expanded(True)
        for book in books:
            expander.add_row(self._make_book_row(book))
        return expander

    def _make_book_row(self, book: BookRecord) -> Adw.ActionRow:
        row = Adw.ActionRow()
        row.set_title(book.title)
        row.set_subtitle(book.author or "Auteur inconnu")
        row.set_activatable(True)
        row.set_title_lines(1)
        row.set_subtitle_lines(1)

        # Couverture
        cover_img = Gtk.Image(pixel_size=_COVER_SIZE, valign=Gtk.Align.CENTER)
        if book.cover_path and Path(book.cover_path).exists():
            try:
                pb = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    book.cover_path, _COVER_SIZE, _COVER_SIZE + 14, True
                )
                cover_img.set_from_pixbuf(pb)
            except Exception:
                cover_img.set_from_icon_name("book-open-variant-symbolic")
        else:
            cover_img.set_from_icon_name("book-open-variant-symbolic")
        row.add_prefix(cover_img)

        # Bouton menu contextuel
        menu_btn = Gtk.MenuButton(
            icon_name="view-more-symbolic",
            tooltip_text="Options",
            valign=Gtk.Align.CENTER,
            css_classes=["flat"],
        )
        menu_btn.set_popover(self._make_book_popover(book))
        row.add_suffix(menu_btn)

        row.connect("activated", lambda _r: self.emit("book-selected", book.file_path))
        return row

    def _make_book_popover(self, book: BookRecord) -> Gtk.Popover:
        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=2,
            margin_top=6, margin_bottom=6, margin_start=6, margin_end=6,
        )

        folders = self._library.all_folders()
        available = [f for f in folders if f.id != book.folder_id]

        if available:
            box.append(Gtk.Label(
                label="Déplacer vers",
                halign=Gtk.Align.START,
                css_classes=["caption", "dim-label"],
                margin_bottom=2,
            ))
            for folder in available:
                btn = Gtk.Button(label=folder.name, css_classes=["flat"],
                                 halign=Gtk.Align.FILL)
                btn.connect("clicked", self._on_move_to_folder, book, folder.id)
                box.append(btn)

        if book.folder_id is not None:
            btn = Gtk.Button(label="Retirer du dossier", css_classes=["flat"],
                             halign=Gtk.Align.FILL)
            btn.connect("clicked", self._on_remove_from_folder, book)
            box.append(btn)

        if available or book.folder_id is not None:
            box.append(Gtk.Separator(
                orientation=Gtk.Orientation.HORIZONTAL,
                margin_top=4, margin_bottom=4,
            ))

        del_btn = Gtk.Button(
            label="Supprimer de la bibliothèque",
            css_classes=["flat", "destructive-action"],
            halign=Gtk.Align.FILL,
        )
        del_btn.connect("clicked", self._on_delete_book, book)
        box.append(del_btn)

        popover = Gtk.Popover(child=box)
        popover.set_has_arrow(True)
        return popover

    # ── handlers livres ───────────────────────────────────────────────────────

    def _on_move_to_folder(self, btn: Gtk.Button, book: BookRecord, folder_id: int) -> None:
        btn.get_ancestor(Gtk.Popover).popdown()
        self._library.move_book_to_folder(book.id, folder_id)
        self.refresh()

    def _on_remove_from_folder(self, btn: Gtk.Button, book: BookRecord) -> None:
        btn.get_ancestor(Gtk.Popover).popdown()
        self._library.move_book_to_folder(book.id, None)
        self.refresh()

    def _on_delete_book(self, btn: Gtk.Button, book: BookRecord) -> None:
        btn.get_ancestor(Gtk.Popover).popdown()
        dialog = Adw.MessageDialog(
            transient_for=self.get_root(),
            heading="Supprimer le livre ?",
            body=f"« {book.title} » sera retiré de la bibliothèque. Le fichier EPUB ne sera pas supprimé.",
        )
        dialog.add_response("cancel", "Annuler")
        dialog.add_response("delete", "Supprimer")
        dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.set_default_response("cancel")
        dialog.set_close_response("cancel")
        dialog.connect("response", lambda d, r: (
            self._library.remove_book(book.id) or self.refresh()
        ) if r == "delete" else None)
        dialog.present()

    # ── handlers dossiers ─────────────────────────────────────────────────────

    def _on_new_folder(self, _btn) -> None:
        entry = Gtk.Entry(placeholder_text="Nom du dossier", activates_default=True)
        entry.set_size_request(240, -1)
        dialog = Adw.MessageDialog(
            transient_for=self.get_root(),
            heading="Nouveau dossier",
        )
        dialog.set_extra_child(entry)
        dialog.add_response("cancel", "Annuler")
        dialog.add_response("create", "Créer")
        dialog.set_response_appearance("create", Adw.ResponseAppearance.SUGGESTED)
        dialog.set_default_response("create")
        dialog.set_close_response("cancel")
        dialog.connect("response", self._on_new_folder_response, entry)
        dialog.present()
        entry.grab_focus()

    def _on_new_folder_response(self, _dialog, response: str, entry: Gtk.Entry) -> None:
        if response == "create":
            name = entry.get_text().strip()
            if name:
                self._library.add_folder(name)
                self.refresh()

    def _on_rename_folder(self, _btn, folder: Folder) -> None:
        entry = Gtk.Entry(text=folder.name, activates_default=True)
        entry.set_size_request(240, -1)
        entry.select_region(0, -1)
        dialog = Adw.MessageDialog(
            transient_for=self.get_root(),
            heading="Renommer le dossier",
        )
        dialog.set_extra_child(entry)
        dialog.add_response("cancel", "Annuler")
        dialog.add_response("rename", "Renommer")
        dialog.set_response_appearance("rename", Adw.ResponseAppearance.SUGGESTED)
        dialog.set_default_response("rename")
        dialog.set_close_response("cancel")
        dialog.connect("response", self._on_rename_folder_response, folder, entry)
        dialog.present()
        entry.grab_focus()

    def _on_rename_folder_response(self, _dialog, response: str,
                                   folder: Folder, entry: Gtk.Entry) -> None:
        if response == "rename":
            name = entry.get_text().strip()
            if name and name != folder.name:
                self._library.rename_folder(folder.id, name)
                self.refresh()

    def _on_delete_folder(self, _btn, folder: Folder) -> None:
        dialog = Adw.MessageDialog(
            transient_for=self.get_root(),
            heading="Supprimer le dossier ?",
            body=f"« {folder.name} » sera supprimé. Les livres seront déplacés dans « Sans dossier ».",
        )
        dialog.add_response("cancel", "Annuler")
        dialog.add_response("delete", "Supprimer")
        dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.set_default_response("cancel")
        dialog.set_close_response("cancel")
        dialog.connect("response", lambda d, r: (
            self._library.remove_folder(folder.id) or self.refresh()
        ) if r == "delete" else None)
        dialog.present()
