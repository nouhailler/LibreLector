"""Data models for EPUB content."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TextSegment:
    """A single word or sentence segment with position info."""

    text: str
    index: int               # position in the chapter's segment list
    char_start: int          # character offset in the chapter plain text
    char_end: int
    # filled in by TTS engine after synthesis
    audio_start_ms: Optional[float] = None
    audio_end_ms: Optional[float] = None


@dataclass
class EpubChapter:
    """One spine item (chapter) from an EPUB."""

    id: str
    title: str
    order: int               # spine order
    html_content: str        # raw HTML from the EPUB
    plain_text: str = ""     # stripped plain text (filled by parser)
    sentences: list[TextSegment] = field(default_factory=list)
    words: list[TextSegment] = field(default_factory=list)


@dataclass
class EpubBook:
    """Parsed representation of an EPUB file."""

    file_path: str
    title: str
    author: str
    language: str
    identifier: str          # unique id from OPF
    cover_path: Optional[str]
    chapters: list[EpubChapter] = field(default_factory=list)
    toc: list[dict] = field(default_factory=list)  # {"title": str, "chapter_id": str}

    @property
    def chapter_count(self) -> int:
        return len(self.chapters)

    def chapter_by_id(self, chapter_id: str) -> Optional[EpubChapter]:
        for ch in self.chapters:
            if ch.id == chapter_id:
                return ch
        return None

    def chapter_by_order(self, order: int) -> Optional[EpubChapter]:
        for ch in self.chapters:
            if ch.order == order:
                return ch
        return None
