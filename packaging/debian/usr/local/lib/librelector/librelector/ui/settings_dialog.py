"""Settings dialog for LibreLector."""
from __future__ import annotations

import json
import logging
from pathlib import Path

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk  # noqa: E402

logger = logging.getLogger(__name__)

_SETTINGS_PATH = Path.home() / ".local" / "share" / "LibreLector" / "settings.json"


class SettingsDialog(Adw.PreferencesDialog):
    """Application settings (TTS engine, voice model, language…)."""

    def __init__(self, **kwargs) -> None:
        super().__init__(title="Paramètres", **kwargs)
        self._settings = self._load()
        self._build()

    # ── build ─────────────────────────────────────────────────────────────────

    def _build(self) -> None:
        page = Adw.PreferencesPage(title="TTS", icon_name="audio-input-microphone-symbolic")
        self.add(page)

        # ── TTS engine group ──────────────────────────────────────────────────
        tts_group = Adw.PreferencesGroup(title="Moteur TTS")
        page.add(tts_group)

        engine_row = Adw.ComboRow(title="Moteur préféré")
        engine_model = Gtk.StringList.new(["piper", "speech_dispatcher"])
        engine_row.set_model(engine_model)
        current_engine = self._settings.get("tts_engine", "speech_dispatcher")
        engine_row.set_selected(0 if current_engine == "piper" else 1)
        engine_row.connect("notify::selected", self._on_engine_changed)
        tts_group.add(engine_row)

        piper_row = Adw.EntryRow(title="Chemin modèle Piper (.onnx)")
        piper_row.set_text(self._settings.get("piper_model", ""))
        piper_row.connect("changed", lambda r: self._set("piper_model", r.get_text()))
        tts_group.add(piper_row)

        # ── Language group ────────────────────────────────────────────────────
        lang_group = Adw.PreferencesGroup(title="Langue")
        page.add(lang_group)

        lang_row = Adw.EntryRow(title="Code langue (ex: fr, en)")
        lang_row.set_text(self._settings.get("language", "fr"))
        lang_row.connect("changed", lambda r: self._set("language", r.get_text()))
        lang_group.add(lang_row)

    # ── persistence ───────────────────────────────────────────────────────────

    def _load(self) -> dict:
        if _SETTINGS_PATH.exists():
            try:
                return json.loads(_SETTINGS_PATH.read_text())
            except Exception:
                pass
        return {}

    def _set(self, key: str, value) -> None:
        self._settings[key] = value
        self._save()

    def _save(self) -> None:
        _SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
        _SETTINGS_PATH.write_text(json.dumps(self._settings, indent=2))

    def _on_engine_changed(self, row: Adw.ComboRow, _param) -> None:
        self._set("tts_engine", "piper" if row.get_selected() == 0 else "speech_dispatcher")
