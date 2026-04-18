"""FB2 (FictionBook 2) document parser.

FB2 is an XML format.  Each top-level <section> inside <body> becomes a
chapter.  Sections without a <title> are labelled automatically.
"""
from __future__ import annotations

import logging
import re
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

from ..epub.models import EpubBook, EpubChapter, TextSegment
from .base import DocumentParser

logger = logging.getLogger(__name__)

# FB2 XML namespace
_NS = "http://www.gribuser.ru/xml/fictionbook/2.0"
_T = f"{{{_NS}}}"


def _tag(name: str) -> str:
    return f"{_T}{name}"


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


def _element_text(el: Optional[ET.Element]) -> str:
    """Recursively gather all text from an XML element."""
    if el is None:
        return ""
    parts: list[str] = []
    if el.text:
        parts.append(el.text.strip())
    for child in el:
        child_text = _element_text(child)
        if child_text:
            parts.append(child_text)
        if child.tail:
            parts.append(child.tail.strip())
    return " ".join(p for p in parts if p)


def _section_plain_text(section: ET.Element) -> str:
    """Extract plain text from a <section>, excluding nested <section>."""
    parts: list[str] = []
    for child in section:
        local = child.tag.replace(_T, "")
        if local == "section":
            continue  # handled recursively
        if local == "title":
            continue  # already used as chapter title
        txt = _element_text(child)
        if txt:
            parts.append(txt)
    text = "\n\n".join(parts)
    return unicodedata.normalize("NFKC", text).strip()


class Fb2DocumentParser(DocumentParser):

    def parse(self, path: str | Path) -> EpubBook:
        path = Path(path)
        logger.info("Parsing FB2: %s", path)

        try:
            tree = ET.parse(str(path))
        except ET.ParseError as exc:
            raise ValueError(f"FB2 XML invalide : {exc}") from exc

        root = tree.getroot()

        # Metadata
        title = self._meta_text(root, "book-title") or path.stem
        author_parts = []
        desc = root.find(_tag("description"))
        if desc is not None:
            ti = desc.find(_tag("title-info"))
            if ti is not None:
                for author_el in ti.findall(_tag("author")):
                    first = (author_el.findtext(_tag("first-name")) or "").strip()
                    last = (author_el.findtext(_tag("last-name")) or "").strip()
                    name = " ".join(p for p in (first, last) if p)
                    if name:
                        author_parts.append(name)
                lang_el = ti.find(_tag("lang"))
                lang = lang_el.text.strip() if lang_el is not None and lang_el.text else "fr"
            else:
                lang = "fr"
        else:
            lang = "fr"

        author = ", ".join(author_parts) or "Auteur inconnu"

        # Body sections
        body = root.find(_tag("body"))
        if body is None:
            raise ValueError("Ce fichier FB2 ne contient pas de <body>.")

        chapters: list[EpubChapter] = []
        toc_out: list[dict] = []
        order = 0

        for section in body.findall(_tag("section")):
            ch_list, toc_list = self._process_section(section, order)
            chapters.extend(ch_list)
            toc_out.extend(toc_list)
            order += len(ch_list)

        return EpubBook(
            file_path=str(path),
            title=title,
            author=author,
            language=lang,
            identifier=path.stem,
            cover_path=None,
            chapters=chapters,
            toc=toc_out,
        )

    def _process_section(
        self, section: ET.Element, base_order: int
    ) -> tuple[list[EpubChapter], list[dict]]:
        """Recursively convert a <section> (and its sub-sections) to chapters."""
        chapters: list[EpubChapter] = []
        toc_out: list[dict] = []

        title_el = section.find(_tag("title"))
        ch_title = _element_text(title_el).strip() if title_el is not None else ""

        plain = _section_plain_text(section)

        if plain:
            order = base_order + len(chapters)
            ch_title = ch_title or f"Section {order + 1}"
            ch = EpubChapter(
                id=f"section_{order}",
                title=ch_title,
                order=order,
                html_content="",
                plain_text=plain,
            )
            _segment_chapter(ch)
            chapters.append(ch)
            toc_out.append({"title": ch_title, "href": ch.id})

        # Nested sections
        for sub in section.findall(_tag("section")):
            sub_chs, sub_toc = self._process_section(sub, base_order + len(chapters))
            chapters.extend(sub_chs)
            toc_out.extend(sub_toc)

        return chapters, toc_out

    @staticmethod
    def _meta_text(root: ET.Element, tag_name: str) -> Optional[str]:
        desc = root.find(_tag("description"))
        if desc is None:
            return None
        ti = desc.find(_tag("title-info"))
        if ti is None:
            return None
        el = ti.find(_tag(tag_name))
        if el is not None and el.text:
            return el.text.strip()
        return None
