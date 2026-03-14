#!/usr/bin/env python3
"""LibreLector – entry point."""
from __future__ import annotations

import logging
import sys


def _configure_logging() -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        level=logging.INFO,
        stream=sys.stderr,
    )


def main() -> int:
    _configure_logging()
    try:
        from .ui.application import LibreLectorApp
        app = LibreLectorApp()
        return app.run_app(sys.argv)
    except ImportError as exc:
        print(
            f"Erreur d'importation GTK/Adwaita : {exc}\n"
            "Installez les dépendances :\n"
            "  sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
