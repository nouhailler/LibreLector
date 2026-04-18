"""Plain-text document parser.

The file is split into chapters at double-blank-line boundaries.
Chapters smaller than ``min_chars`` (default 200) are merged with the next.
"""
from __future__ import annotations

import logging
import re
import unicodedata
from pathlib import Path

from ..epub.models import EpubBook, EpubChapter, TextSegment
from .base import DocumentParser

logger = logging.getLogger(__name__)

_MIN_CHAPTER_CHARS = 200
_MAX_CHAPTER_CHARS = 8_000


def _split_sentences(text: str) -> list[str]:
    try:
        import nltk
        try:
            return nltk.sent_tokenize(text)
        except LookupError:
            nltk.download("punkt_tab", quiet=True)
            return nltk.sent_tokenize(text)
    except ImportError:
        pass
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]


def _segment_chapter(chapter: EpubChapter) -> None:
    sentences_raw = _split_sentences(chapter.plain_text)
    char_cursor = 0
    for idx, sent in enumerate(sentences_raw):
        if not sent.strip():
            continue
        start = chapter.plain_text.find(sent, char_cursor)
        if start == -1:
            start = char_cursor
        end = start + len(sent)
        chapter.sentences.append(TextSegment(
            text=sent, index=idx, char_start=start, char_end=end,
        ))
        char_cursor = end


class TxtDocumentParser(DocumentParser):

    def __init__(
        self,
        min_chapter_chars: int = _MIN_CHAPTER_CHARS,
        max_chapter_chars: int = _MAX_CHAPTER_CHARS,
    ) -> None:
        self.min_chapter_chars = min_chapter_chars
        self.max_chapter_chars = max_chapter_chars

    def parse(self, path: str | Path) -> EpubBook:
        path = Path(path)
        logger.info("Parsing TXT: %s", path)

        try:
            raw = path.read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            raise ValueError(f"Impossible de lire le fichier texte : {exc}") from exc

        raw = unicodedata.normalize("NFKC", raw)
        title = path.stem.replace("_", " ").replace("-", " ").title()

        # Split on double newlines
        blocks = re.split(r'\n{2,}', raw)
        # Merge short blocks, split overly long ones
        sections = self._consolidate(blocks)

        chapters: list[EpubChapter] = []
        toc_out: list[dict] = []

        for order, text in enumerate(sections):
            text = text.strip()
            if not text:
                continue
            # Use first line as title if it looks like a heading (short, no period)
            first_line = text.split("\n", 1)[0].strip()
            if len(first_line) < 80 and not first_line.endswith((".", "!", "?")):
                ch_title = first_line or f"Section {order + 1}"
            else:
                ch_title = f"Section {order + 1}"

            ch = EpubChapter(
                id=f"section_{order}",
                title=ch_title,
                order=order,
                html_content="",
                plain_text=text,
            )
            _segment_chapter(ch)
            chapters.append(ch)
            toc_out.append({"title": ch_title, "href": ch.id})

        return EpubBook(
            file_path=str(path),
            title=title,
            author="Auteur inconnu",
            language="fr",
            identifier=path.stem,
            cover_path=None,
            chapters=chapters,
            toc=toc_out,
        )

    def _consolidate(self, blocks: list[str]) -> list[str]:
        """Merge short blocks and split blocks that exceed max_chapter_chars."""
        merged: list[str] = []
        buf = ""
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            buf = (buf + "\n\n" + block).strip() if buf else block
            if len(buf) >= self.min_chapter_chars:
                if len(buf) > self.max_chapter_chars:
                    # Hard-split at sentence or character boundary
                    merged.extend(self._hard_split(buf))
                    buf = ""
                else:
                    merged.append(buf)
                    buf = ""
        if buf:
            merged.append(buf)
        return merged

    def _hard_split(self, text: str) -> list[str]:
        """Split *text* into chunks of at most max_chapter_chars."""
        parts: list[str] = []
        while len(text) > self.max_chapter_chars:
            cut = text.rfind(" ", 0, self.max_chapter_chars)
            if cut == -1:
                cut = self.max_chapter_chars
            parts.append(text[:cut].strip())
            text = text[cut:].strip()
        if text:
            parts.append(text)
        return parts
