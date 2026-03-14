"""User-defined pronunciation dictionary.

Stored as JSON:
{
    "LLM": "L L M",
    "Kubernetes": "koubernetesse"
}
"""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

_DEFAULT_PATH = Path.home() / ".local" / "share" / "LibreLector" / "pronunciation.json"


class PronunciationDict:
    """Load and apply a user pronunciation dictionary."""

    def __init__(self, path: Optional[str | Path] = None) -> None:
        self._path = Path(path) if path else _DEFAULT_PATH
        self._dict: dict[str, str] = {}
        self.load()

    def load(self) -> None:
        if self._path.exists():
            try:
                self._dict = json.loads(self._path.read_text(encoding="utf-8"))
                logger.debug("Loaded %d pronunciations", len(self._dict))
            except Exception as exc:
                logger.warning("Could not load pronunciation dict: %s", exc)

    def save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps(self._dict, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def add(self, word: str, pronunciation: str) -> None:
        self._dict[word] = pronunciation
        self.save()

    def remove(self, word: str) -> None:
        self._dict.pop(word, None)
        self.save()

    def apply(self, text: str) -> str:
        """Replace known words in *text* with their phonetic equivalents."""
        for word, replacement in self._dict.items():
            pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
            text = pattern.sub(replacement, text)
        return text

    @property
    def entries(self) -> dict[str, str]:
        return dict(self._dict)
