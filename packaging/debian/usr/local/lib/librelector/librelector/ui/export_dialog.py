"""Export progress dialog."""
from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Optional

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, GLib, Gtk

logger = logging.getLogger(__name__)


class ExportDialog(Adw.Dialog):
    """Modal dialog showing MP3 export progress."""

    def __init__(self, book, model_path: str, output_dir: str, **kwargs):
        super().__init__(**kwargs)
        self._book = book
        self._model_path = model_path
        self._output_dir = output_dir
        self._stop = False
        self._thread: Optional[threading.Thread] = None

        self.set_title("Export MP3")
        self.set_content_width(400)

        # Layout
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16,
                      margin_top=24, margin_bottom=24,
                      margin_start=24, margin_end=24)

        self._status_label = Gtk.Label(label="Initialisation…", wrap=True,
                                       halign=Gtk.Align.START)
        box.append(self._status_label)

        self._progress = Gtk.ProgressBar(show_text=True)
        box.append(self._progress)

        self._detail_label = Gtk.Label(label="", wrap=True,
                                       halign=Gtk.Align.START,
                                       css_classes=["dim-label"])
        box.append(self._detail_label)

        # Buttons
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,
                          spacing=8, halign=Gtk.Align.END)
        self._btn_cancel = Gtk.Button(label="Annuler")
        self._btn_cancel.connect("clicked", self._on_cancel)
        btn_box.append(self._btn_cancel)

        self._btn_close = Gtk.Button(label="Fermer", css_classes=["suggested-action"])
        self._btn_close.set_sensitive(False)
        self._btn_close.connect("clicked", lambda _: self.close())
        btn_box.append(self._btn_close)

        box.append(btn_box)
        self.set_child(box)

    def start(self, parent) -> None:
        self.present(parent)
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        from ..core.exporter import Mp3Exporter
        exporter = Mp3Exporter(self._model_path)

        if not exporter.is_available():
            GLib.idle_add(self._set_error, "Piper ou ffmpeg introuvable.")
            return

        GLib.idle_add(self._status_label.set_label,
                      f"Export vers : {self._output_dir}")

        def progress(cur, total, title):
            frac = cur / total
            GLib.idle_add(self._progress.set_fraction, frac)
            GLib.idle_add(self._progress.set_text, f"{cur}/{total}")
            GLib.idle_add(self._detail_label.set_label, title)

        results = exporter.export_book(
            self._book,
            self._output_dir,
            progress_cb=progress,
            stop_flag=lambda: self._stop,
        )

        if self._stop:
            GLib.idle_add(self._set_done, "Export annulé.", len(results))
        else:
            GLib.idle_add(self._set_done, "Export terminé ✓", len(results))

    def _set_done(self, msg: str, count: int) -> None:
        self._status_label.set_label(msg)
        self._detail_label.set_label(f"{count} fichier(s) MP3 créé(s) dans {self._output_dir}")
        self._progress.set_fraction(1.0)
        self._btn_cancel.set_sensitive(False)
        self._btn_close.set_sensitive(True)

    def _set_error(self, msg: str) -> None:
        self._status_label.set_label(f"Erreur : {msg}")
        self._btn_cancel.set_sensitive(False)
        self._btn_close.set_sensitive(True)

    def _on_cancel(self, _btn) -> None:
        self._stop = True
        self._btn_cancel.set_sensitive(False)
        self._status_label.set_label("Annulation en cours…")
