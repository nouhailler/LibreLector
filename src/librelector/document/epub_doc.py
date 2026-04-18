"""EPUB document parser — thin wrapper around the existing EpubParser."""
from __future__ import annotations

from pathlib import Path

from ..epub.models import EpubBook
from ..epub.parser import EpubParser
from .base import DocumentParser


class EpubDocumentParser(DocumentParser):

    def __init__(self, min_chapter_chars: int = 100) -> None:
        self._inner = EpubParser(min_chapter_chars=min_chapter_chars)

    def parse(self, path: str | Path) -> EpubBook:
        return self._inner.parse(path)
