"""Main GTK4 / Libadwaita application class."""
from __future__ import annotations

import logging
import sys

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio, Gtk  # noqa: E402

from .window import MainWindow

logger = logging.getLogger(__name__)

APP_ID = "io.github.librelector"


class LibreLectorApp(Adw.Application):
    """Top-level Adwaita application."""

    def __init__(self) -> None:
        super().__init__(
            application_id=APP_ID,
            flags=Gio.ApplicationFlags.HANDLES_OPEN,
        )
        self._window: MainWindow | None = None
        self.connect("activate", self._on_activate)
        self.connect("open", self._on_open)

    # ── GTK signal handlers ───────────────────────────────────────────────────

    def _on_activate(self, app: Adw.Application) -> None:
        if self._window is None:
            self._window = MainWindow(application=app)
        self._window.present()

    def _on_open(self, app: Adw.Application, files: list, _hint: str) -> None:
        self._on_activate(app)
        if files:
            self._window.open_file(files[0].get_path())

    # ── entry point ───────────────────────────────────────────────────────────

    def run_app(self, argv: list[str] | None = None) -> int:
        return self.run(argv or sys.argv)
