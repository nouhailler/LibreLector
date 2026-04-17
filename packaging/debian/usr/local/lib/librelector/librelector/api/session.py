"""Global application session — singleton shared by all routers."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

from ..data.library import Library
from ..core.player import Player
from ..tts.factory import create_engine
from .ws_manager import WebSocketManager

logger = logging.getLogger(__name__)

_SETTINGS_PATH = Path.home() / ".local" / "share" / "LibreLector" / "settings.json"
_VOICES_DIR = Path.home() / ".local" / "share" / "LibreLector" / "voices"

_DEFAULT_SETTINGS: dict = {
    "tts_engine": "piper",
    "piper_model": "",
    "language": "fr",
}


class AppSession:
    """Holds all long-lived application objects."""

    def __init__(self) -> None:
        self.library: Library = Library()
        self.settings: dict = {}
        self.player: Optional[Player] = None
        self.ws_manager: WebSocketManager = WebSocketManager()
        self.load_settings()

    # ── settings ──────────────────────────────────────────────────────────────

    def load_settings(self) -> dict:
        """Load (or reload) settings from disk."""
        if _SETTINGS_PATH.exists():
            try:
                with _SETTINGS_PATH.open("r", encoding="utf-8") as fh:
                    data = json.load(fh)
                self.settings = {**_DEFAULT_SETTINGS, **data}
                logger.info("Settings loaded from %s", _SETTINGS_PATH)
            except Exception as exc:
                logger.error("settings.json invalide : %s — defaults used", exc)
                self.settings = dict(_DEFAULT_SETTINGS)
        else:
            self.settings = dict(_DEFAULT_SETTINGS)
        return self.settings

    def save_settings(self, data: dict) -> None:
        """Persist *data* to disk and reinitialise the TTS engine."""
        self.settings = {**_DEFAULT_SETTINGS, **data}
        _SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with _SETTINGS_PATH.open("w", encoding="utf-8") as fh:
            json.dump(self.settings, fh, ensure_ascii=False, indent=2)
        logger.info("Settings saved to %s", _SETTINGS_PATH)

        # Reinitialise player with new engine if a book is loaded
        if self.player is not None and self.player.book is not None:
            book_path = self.player.book.file_path
            self.init_player()
            try:
                self.player.open_book(book_path)
            except Exception as exc:
                logger.error("Impossible de rouvrir le livre après changement de settings: %s", exc)

    # ── player ────────────────────────────────────────────────────────────────

    def init_player(self) -> Player:
        """Create (or recreate) a Player with the current TTS settings."""
        engine = create_engine(
            preferred=self.settings.get("tts_engine", "piper"),
            piper_model=self.settings.get("piper_model") or None,
            language=self.settings.get("language", "fr"),
        )
        player = Player(engine=engine, library=self.library)

        ws = self.ws_manager

        player.set_on_sentence(lambda idx: ws.broadcast({"type": "sentence", "index": idx}))
        player.set_on_state(lambda state: ws.broadcast({"type": "state", "value": state.name.lower()}))
        player.set_on_chapter(lambda ch: ws.broadcast({"type": "chapter", "order": ch.order}))

        self.player = player
        logger.info("Player initialised")
        return player

    # ── voices ────────────────────────────────────────────────────────────────

    def list_voices(self) -> list[dict]:
        """Return a list of available Piper voice models."""
        if not _VOICES_DIR.exists():
            return []
        return [
            {"name": p.stem, "path": str(p)}
            for p in sorted(_VOICES_DIR.glob("*.onnx"))
        ]
