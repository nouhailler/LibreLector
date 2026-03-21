"""EPUB parser: ZIP → OPF → HTML → plain text → segments."""
from __future__ import annotations

import logging
import re
import unicodedata
from pathlib import Path
from typing import Optional

import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from bs4 import XMLParsedAsHTMLWarning
import warnings
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

from .models import EpubBook, EpubChapter, TextSegment

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Sentence tokenisation (no NLTK dependency at import time)
# ──────────────────────────────────────────────────────────────────────────────

# Simple regex-based sentence splitter used as fallback when NLTK is absent.
_SENTENCE_RE = re.compile(r'(?<=[.!?])\s+')


def _split_sentences(text: str) -> list[str]:
    """Split *text* into sentences using NLTK if available, else regex."""
    try:
        import nltk
        try:
            return nltk.sent_tokenize(text)
        except LookupError:
            nltk.download("punkt", quiet=True)
            nltk.download("punkt_tab", quiet=True)
            return nltk.sent_tokenize(text)
    except ImportError:
        pass
    return [s.strip() for s in _SENTENCE_RE.split(text) if s.strip()]


def _split_words(sentence: str) -> list[str]:
    """Return individual word tokens from a sentence."""
    return [w for w in re.split(r'(\s+)', sentence) if w.strip()]


# ──────────────────────────────────────────────────────────────────────────────
# HTML → plain text
# ──────────────────────────────────────────────────────────────────────────────

_BLOCK_TAGS = {
    "p", "div", "h1", "h2", "h3", "h4", "h5", "h6",
    "li", "td", "th", "blockquote", "section", "article",
    "header", "footer", "aside", "main",
}


def _html_to_text(html: str) -> str:
    """Convert HTML to plain text, preserving paragraph breaks."""
    soup = BeautifulSoup(html, "lxml")

    # Insert newlines before block-level tags so paragraphs are separated.
    for tag in soup.find_all(_BLOCK_TAGS):
        tag.insert_before("\n")
        tag.append("\n")

    text = soup.get_text(separator="")
    # Collapse multiple blank lines to one
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Normalise unicode spaces / hyphens
    text = unicodedata.normalize("NFKC", text)
    return text.strip()


# ──────────────────────────────────────────────────────────────────────────────
# Main parser class
# ──────────────────────────────────────────────────────────────────────────────

class EpubParser:
    """Parse an EPUB file and return an :class:`EpubBook` instance."""

    def __init__(self, min_chapter_chars: int = 100):
        """
        Parameters
        ----------
        min_chapter_chars:
            Chapters whose plain text is shorter than this are considered
            navigation artefacts and skipped.
        """
        self.min_chapter_chars = min_chapter_chars

    # ── public API ───────────────────────────────────────────────────────────

    def parse(self, epub_path: str | Path) -> EpubBook:
        """Parse *epub_path* and return a fully populated :class:`EpubBook`."""
        epub_path = Path(epub_path)
        logger.info("Parsing EPUB: %s", epub_path)

        book = epub.read_epub(str(epub_path), options={"ignore_ncx": False})

        title  = self._meta(book, "title")  or epub_path.stem
        author = self._meta(book, "creator") or "Auteur inconnu"
        lang   = self._meta(book, "language") or "fr"
        uid    = self._meta(book, "identifier") or epub_path.stem

        cover_path = self._extract_cover(book, epub_path)
        chapters   = self._build_chapters(book)
        toc        = self._build_toc(book, chapters)

        return EpubBook(
            file_path=str(epub_path),
            title=title,
            author=author,
            language=lang,
            identifier=uid,
            cover_path=cover_path,
            chapters=chapters,
            toc=toc,
        )

    def _build_toc(self, book: epub.EpubBook, chapters: list[EpubChapter]) -> list[dict]:
        """Build a table of contents from the EPUB NCX/NAV or chapter list."""
        toc = []
        try:
            for item in book.toc:
                if hasattr(item, 'title') and hasattr(item, 'href'):
                    toc.append({"title": item.title, "href": item.href})
                elif isinstance(item, tuple) and len(item) == 2:
                    section, children = item
                    toc.append({"title": section.title, "href": section.href})
        except Exception as exc:
            logger.debug("TOC extraction failed: %s", exc)

        if not toc:
            toc = [{"title": ch.title, "href": ch.id} for ch in chapters]

        return toc

    # ── private helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _meta(book: epub.EpubBook, name: str) -> Optional[str]:
        items = book.get_metadata("DC", name)
        if items:
            val = items[0]
            return str(val[0]).strip() if isinstance(val, tuple) else str(val).strip()
        return None

    def _extract_cover(self, book: epub.EpubBook, epub_path: Path) -> Optional[str]:
        """Extract cover image next to the EPUB file and return its path."""
        cover_item = None

        # Try manifest item marked as cover-image
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_COVER:
                cover_item = item
                break

        # Fallback: look for an item whose id is "cover"
        if cover_item is None:
            cover_item = book.get_item_with_id("cover")

        if cover_item is None:
            return None

        suffix = Path(cover_item.file_name).suffix or ".jpg"
        cover_out = epub_path.parent / (epub_path.stem + "_cover" + suffix)
        try:
            cover_out.write_bytes(cover_item.get_content())
            return str(cover_out)
        except Exception as exc:
            logger.warning("Could not write cover: %s", exc)
            return None

    def _build_chapters(self, book: epub.EpubBook) -> list[EpubChapter]:
        chapters: list[EpubChapter] = []
        order = 0

        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            html = item.get_content().decode("utf-8", errors="replace")
            plain = _html_to_text(html)

            if len(plain) < self.min_chapter_chars:
                logger.debug("Skipping short chapter %s (%d chars)", item.id, len(plain))
                continue

            title = self._infer_chapter_title(html, item.id, order)
            chapter = EpubChapter(
                id=item.id,
                title=title,
                order=order,
                html_content=html,
                plain_text=plain,
            )
            self._segment(chapter)
            chapters.append(chapter)
            order += 1

        return chapters

    @staticmethod
    def _infer_chapter_title(html: str, fallback_id: str, order: int) -> str:
        soup = BeautifulSoup(html, "lxml")
        for tag in ("h1", "h2", "h3"):
            el = soup.find(tag)
            if el and el.get_text(strip=True):
                return el.get_text(strip=True)
        return f"Chapitre {order + 1}"

    @staticmethod
    def _segment(chapter: EpubChapter) -> None:
        """Populate *chapter.sentences* and *chapter.words* in-place."""
        sentences_raw = _split_sentences(chapter.plain_text)
        char_cursor = 0
        sentence_idx = 0
        word_idx = 0

        for sent_text in sentences_raw:
            if not sent_text.strip():
                continue

            # Locate this sentence in the full plain text (approximate)
            start = chapter.plain_text.find(sent_text, char_cursor)
            if start == -1:
                start = char_cursor
            end = start + len(sent_text)

            chapter.sentences.append(TextSegment(
                text=sent_text,
                index=sentence_idx,
                char_start=start,
                char_end=end,
            ))
            sentence_idx += 1

            # Word-level segmentation within the sentence
            words = _split_words(sent_text)
            w_cursor = start
            for word in words:
                w_start = chapter.plain_text.find(word, w_cursor)
                if w_start == -1:
                    w_start = w_cursor
                w_end = w_start + len(word)
                chapter.words.append(TextSegment(
                    text=word,
                    index=word_idx,
                    char_start=w_start,
                    char_end=w_end,
                ))
                word_idx += 1
                w_cursor = w_end

            char_cursor = end
