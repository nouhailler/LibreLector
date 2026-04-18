"""Abstract document parser interface."""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from ..epub.models import EpubBook


class DocumentParser(ABC):
    """Base class for all format-specific parsers.

    Every subclass must implement :meth:`parse` which returns an
    :class:`~librelector.epub.models.EpubBook`.  The rest of the application
    (Player, TTS, exporter) works exclusively with ``EpubBook`` objects, so
    this abstraction lets non-EPUB formats plug in without touching any other
    layer.
    """

    @abstractmethod
    def parse(self, path: str | Path) -> EpubBook:
        """Parse *path* and return a fully populated EpubBook."""
