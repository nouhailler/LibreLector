"""Unit tests for PronunciationDict."""
import pytest
from pathlib import Path
from librelector.core.pronunciation import PronunciationDict


@pytest.fixture
def pdict(tmp_path):
    p = tmp_path / "pronunciation.json"
    return PronunciationDict(path=p)


class TestPronunciationDict:
    def test_add_and_apply(self, pdict):
        pdict.add("LLM", "L L M")
        result = pdict.apply("Le LLM est utile.")
        assert "L L M" in result

    def test_case_insensitive(self, pdict):
        pdict.add("LLM", "L L M")
        result = pdict.apply("le llm est utile.")
        assert "L L M" in result

    def test_remove(self, pdict):
        pdict.add("LLM", "L L M")
        pdict.remove("LLM")
        result = pdict.apply("Le LLM est utile.")
        assert "LLM" in result

    def test_persistence(self, tmp_path):
        p = tmp_path / "pron.json"
        d1 = PronunciationDict(path=p)
        d1.add("CPU", "cépéu")
        d2 = PronunciationDict(path=p)
        assert "CPU" in d2.entries

    def test_no_partial_match(self, pdict):
        pdict.add("AI", "A I")
        result = pdict.apply("RAIN is wet.")
        assert "RAIN" in result   # should NOT replace AI inside RAIN
