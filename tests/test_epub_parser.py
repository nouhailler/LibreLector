"""Unit tests for the EPUB parser (no real EPUB file needed for basic logic)."""
import pytest

from librelector.epub.parser import _html_to_text, _split_sentences, _split_words
from librelector.epub.models import EpubChapter, TextSegment


class TestHtmlToText:
    def test_strips_tags(self):
        html = "<p>Bonjour <strong>monde</strong>!</p>"
        result = _html_to_text(html)
        assert "Bonjour" in result
        assert "monde" in result
        assert "<" not in result

    def test_paragraph_separation(self):
        html = "<p>Premier.</p><p>Second.</p>"
        result = _html_to_text(html)
        assert "\n" in result

    def test_empty_html(self):
        assert _html_to_text("") == ""

    def test_heading_extracted(self):
        html = "<h1>Titre</h1><p>Contenu du chapitre.</p>"
        result = _html_to_text(html)
        assert "Titre" in result
        assert "Contenu" in result


class TestSplitSentences:
    def test_basic(self):
        text = "Bonjour. Comment allez-vous? Très bien."
        sents = _split_sentences(text)
        assert len(sents) >= 2

    def test_single_sentence(self):
        text = "Une seule phrase sans point final"
        sents = _split_sentences(text)
        assert len(sents) == 1
        assert sents[0] == text


class TestSplitWords:
    def test_basic(self):
        words = _split_words("Bonjour monde")
        assert "Bonjour" in words
        assert "monde" in words

    def test_punctuation_attached(self):
        words = _split_words("Fin.")
        assert any("Fin" in w for w in words)

    def test_empty(self):
        assert _split_words("") == []


class TestEpubChapterSegment:
    def test_segments_populated(self):
        from librelector.epub.parser import EpubParser
        chapter = EpubChapter(
            id="ch1",
            title="Test",
            order=0,
            html_content="<p>Bonjour monde. Au revoir.</p>",
            plain_text="Bonjour monde. Au revoir.",
        )
        EpubParser._segment(chapter)
        assert len(chapter.sentences) >= 1
        assert len(chapter.words) >= 1

    def test_segment_char_offsets(self):
        from librelector.epub.parser import EpubParser
        chapter = EpubChapter(
            id="ch1", title="T", order=0,
            html_content="", plain_text="Hello world. Goodbye.",
        )
        EpubParser._segment(chapter)
        for seg in chapter.sentences:
            assert seg.char_start >= 0
            assert seg.char_end > seg.char_start
