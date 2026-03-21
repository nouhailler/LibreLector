"""EPUB parsing module."""
from .parser import EpubParser
from .models import EpubBook, EpubChapter, TextSegment

__all__ = ["EpubParser", "EpubBook", "EpubChapter", "TextSegment"]
