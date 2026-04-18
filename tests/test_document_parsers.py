"""Tests for multi-format document parsers."""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from librelector.document.factory import load_document, SUPPORTED_EXTENSIONS
from librelector.document.txt_doc import TxtDocumentParser
from librelector.document.fb2_doc import Fb2DocumentParser


# ── Helpers ───────────────────────────────────────────────────────────────────

def _write(tmp_path: Path, name: str, content: str | bytes, mode: str = "w") -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8") if mode == "w" else p.write_bytes(content)
    return p


# ── TXT parser ────────────────────────────────────────────────────────────────

class TestTxtParser:

    def test_basic_parse(self, tmp_path):
        # Each section must exceed min_chapter_chars (200) to become its own chapter
        section_a = "Phrase A. " * 30   # ~300 chars
        section_b = "Phrase B. " * 30   # ~300 chars
        content = f"Chapitre Un\n\n{section_a}\n\nChapitre Deux\n\n{section_b}"
        p = _write(tmp_path, "story.txt", content)
        book = TxtDocumentParser().parse(p)

        assert book.title == "Story"
        assert len(book.chapters) >= 2

    def test_chapters_have_sentences(self, tmp_path):
        content = "Section A\n\n" + ("Phrase numéro un. " * 10) + "\n\n" + "Section B\n\n" + ("Phrase deux. " * 10)
        p = _write(tmp_path, "sample.txt", content)
        book = TxtDocumentParser().parse(p)

        for ch in book.chapters:
            assert len(ch.sentences) > 0
            assert ch.plain_text.strip()

    def test_hard_split_long_block(self, tmp_path):
        long_text = "Mot. " * 2000  # > 8000 chars
        p = _write(tmp_path, "long.txt", long_text)
        book = TxtDocumentParser(max_chapter_chars=500).parse(p)
        # Should have been split into multiple chapters
        assert len(book.chapters) > 1
        for ch in book.chapters:
            assert len(ch.plain_text) <= 600  # some slack for word boundary


# ── FB2 parser ────────────────────────────────────────────────────────────────

_FB2_SAMPLE = """\
<?xml version="1.0" encoding="utf-8"?>
<FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0">
  <description>
    <title-info>
      <author>
        <first-name>Jean</first-name>
        <last-name>Dupont</last-name>
      </author>
      <book-title>Mon Roman FB2</book-title>
      <lang>fr</lang>
    </title-info>
  </description>
  <body>
    <section>
      <title><p>Chapitre Un</p></title>
      <p>Il était une fois, dans un pays lointain, un héros courageux.</p>
      <p>Ce héros avait de nombreuses aventures et défis à surmonter chaque jour.</p>
    </section>
    <section>
      <title><p>Chapitre Deux</p></title>
      <p>La suite des événements fut encore plus palpitante et inattendue pour tous.</p>
    </section>
  </body>
</FictionBook>
"""


class TestFb2Parser:

    def test_basic_parse(self, tmp_path):
        p = _write(tmp_path, "book.fb2", _FB2_SAMPLE)
        book = Fb2DocumentParser().parse(p)

        assert book.title == "Mon Roman FB2"
        assert book.author == "Jean Dupont"
        assert book.language == "fr"
        assert len(book.chapters) == 2
        assert book.chapters[0].title == "Chapitre Un"
        assert book.chapters[1].title == "Chapitre Deux"

    def test_sentences_populated(self, tmp_path):
        p = _write(tmp_path, "book.fb2", _FB2_SAMPLE)
        book = Fb2DocumentParser().parse(p)
        for ch in book.chapters:
            assert len(ch.sentences) > 0

    def test_invalid_xml_raises(self, tmp_path):
        p = _write(tmp_path, "bad.fb2", "<not valid xml >>>")
        with pytest.raises(ValueError, match="FB2 XML invalide"):
            Fb2DocumentParser().parse(p)


# ── Factory ───────────────────────────────────────────────────────────────────

class TestFactory:

    def test_supported_extensions(self):
        assert ".epub" in SUPPORTED_EXTENSIONS
        assert ".pdf" in SUPPORTED_EXTENSIONS
        assert ".txt" in SUPPORTED_EXTENSIONS
        assert ".fb2" in SUPPORTED_EXTENSIONS

    def test_txt_via_factory(self, tmp_path):
        content = "Section\n\n" + "Texte de la section. " * 20
        p = _write(tmp_path, "test.txt", content)
        book = load_document(p)
        assert len(book.chapters) >= 1

    def test_fb2_via_factory(self, tmp_path):
        p = _write(tmp_path, "test.fb2", _FB2_SAMPLE)
        book = load_document(p)
        assert book.title == "Mon Roman FB2"

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_document(tmp_path / "nonexistent.txt")

    def test_unsupported_format_raises(self, tmp_path):
        p = _write(tmp_path, "file.xyz", "content")
        with pytest.raises(ValueError, match="Format non reconnu"):
            load_document(p)
