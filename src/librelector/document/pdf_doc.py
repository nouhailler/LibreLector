"""PDF document parser using PyMuPDF (fitz).

Pages are grouped into chapters of at most ``pages_per_chapter`` pages
(default 10).  If the PDF contains a table of contents, chapter boundaries
are derived from it instead.
"""
from __future__ import annotations

import logging
import re
import unicodedata
from pathlib import Path
from typing import Optional

from ..epub.models import EpubBook, EpubChapter, TextSegment
from .base import DocumentParser

logger = logging.getLogger(__name__)

_PAGES_PER_CHAPTER = 10


def _require_fitz():
    try:
        import fitz  # PyMuPDF
        return fitz
    except ImportError as exc:
        raise ImportError(
            "PyMuPDF est requis pour lire les PDF. "
            "Installez-le avec : pip install PyMuPDF"
        ) from exc


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
    """Fill chapter.sentences in-place (word-level segmentation omitted for PDFs)."""
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


class PdfDocumentParser(DocumentParser):
    """Parse a PDF file into an EpubBook (one chapter per page group)."""

    def __init__(self, pages_per_chapter: int = _PAGES_PER_CHAPTER) -> None:
        self.pages_per_chapter = pages_per_chapter

    def parse(self, path: str | Path) -> EpubBook:
        fitz = _require_fitz()
        path = Path(path)
        logger.info("Parsing PDF: %s", path)

        try:
            doc = fitz.open(str(path))
        except Exception as exc:
            raise ValueError(f"Impossible d'ouvrir le PDF : {exc}") from exc

        title = doc.metadata.get("title") or path.stem
        author = doc.metadata.get("author") or "Auteur inconnu"
        language = doc.metadata.get("language") or "fr"

        # Build page text list lazily (do not load all pages into RAM at once)
        page_texts: list[str] = []
        for page in doc:
            text = page.get_text("text")
            text = unicodedata.normalize("NFKC", text).strip()
            if text:
                page_texts.append(text)
            else:
                page_texts.append("")  # keep index aligned

        # Try to derive chapter boundaries from the PDF TOC
        toc_entries = doc.get_toc(simple=True)  # [(level, title, page_no), ...]
        chapters: list[EpubChapter] = []
        toc_out: list[dict] = []

        if toc_entries:
            chapters, toc_out = self._chapters_from_toc(
                toc_entries, page_texts, path.stem
            )
        else:
            chapters, toc_out = self._chapters_from_pages(page_texts)

        doc.close()

        return EpubBook(
            file_path=str(path),
            title=title,
            author=author,
            language=language,
            identifier=path.stem,
            cover_path=None,
            chapters=chapters,
            toc=toc_out,
        )

    def _chapters_from_toc(
        self,
        toc: list,
        page_texts: list[str],
        fallback_stem: str,
    ) -> tuple[list[EpubChapter], list[dict]]:
        # toc: [(level, title, 1-based page_no), ...]
        top_entries = [(t, p - 1) for lvl, t, p in toc if lvl == 1]
        if not top_entries:
            top_entries = [(t, p - 1) for lvl, t, p in toc]

        chapters: list[EpubChapter] = []
        toc_out: list[dict] = []

        for order, (entry_title, start_page) in enumerate(top_entries):
            end_page = (
                top_entries[order + 1][1]
                if order + 1 < len(top_entries)
                else len(page_texts)
            )
            plain = "\n\n".join(
                t for t in page_texts[start_page:end_page] if t
            )
            if not plain.strip():
                continue
            ch = EpubChapter(
                id=f"chapter_{order}",
                title=entry_title or f"Chapitre {order + 1}",
                order=order,
                html_content="",
                plain_text=plain,
            )
            _segment_chapter(ch)
            chapters.append(ch)
            toc_out.append({"title": ch.title, "href": ch.id})

        return chapters, toc_out

    def _chapters_from_pages(
        self, page_texts: list[str]
    ) -> tuple[list[EpubChapter], list[dict]]:
        n = self.pages_per_chapter
        groups = [page_texts[i : i + n] for i in range(0, len(page_texts), n)]
        chapters: list[EpubChapter] = []
        toc_out: list[dict] = []

        for order, group in enumerate(groups):
            plain = "\n\n".join(t for t in group if t)
            if not plain.strip():
                continue
            title = f"Pages {order * n + 1}–{min((order + 1) * n, len(page_texts))}"
            ch = EpubChapter(
                id=f"chapter_{order}",
                title=title,
                order=order,
                html_content="",
                plain_text=plain,
            )
            _segment_chapter(ch)
            chapters.append(ch)
            toc_out.append({"title": title, "href": ch.id})

        return chapters, toc_out
