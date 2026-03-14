"""Unit tests for the Library (SQLite) module."""
import tempfile
from pathlib import Path
import pytest

from librelector.data.library import Library
from librelector.data.models import BookRecord, ReadingProgress, Bookmark


@pytest.fixture
def lib(tmp_path):
    db = tmp_path / "test.db"
    library = Library(db_path=db)
    yield library
    library.close()


def _make_record(path="/tmp/test.epub") -> BookRecord:
    return BookRecord(
        id=None,
        file_path=path,
        title="Mon Livre",
        author="Auteur Test",
        language="fr",
        identifier="isbn-001",
        cover_path=None,
        chapter_count=5,
        added_at="2024-01-01T00:00:00+00:00",
    )


class TestBooks:
    def test_add_and_retrieve(self, lib):
        rec = lib.add_book(_make_record())
        assert rec.id is not None
        fetched = lib.get_book(rec.id)
        assert fetched.title == "Mon Livre"
        assert fetched.author == "Auteur Test"

    def test_upsert(self, lib):
        r1 = lib.add_book(_make_record())
        r2 = lib.add_book(_make_record())   # same path → update
        assert r1.id == r2.id
        assert len(lib.all_books()) == 1

    def test_remove(self, lib):
        rec = lib.add_book(_make_record())
        lib.remove_book(rec.id)
        assert lib.get_book(rec.id) is None

    def test_all_books_empty(self, lib):
        assert lib.all_books() == []

    def test_get_by_path(self, lib):
        lib.add_book(_make_record("/tmp/a.epub"))
        found = lib.get_book_by_path("/tmp/a.epub")
        assert found is not None
        assert found.title == "Mon Livre"


class TestProgress:
    def test_save_and_load(self, lib):
        rec = lib.add_book(_make_record())
        progress = ReadingProgress(
            book_id=rec.id,
            chapter_order=2,
            sentence_index=10,
            char_offset=500,
            audio_ms=12345.6,
            updated_at="2024-01-02T00:00:00+00:00",
        )
        lib.save_progress(progress)
        loaded = lib.get_progress(rec.id)
        assert loaded.chapter_order == 2
        assert loaded.sentence_index == 10

    def test_upsert_progress(self, lib):
        rec = lib.add_book(_make_record())
        for i in range(3):
            lib.save_progress(ReadingProgress(
                book_id=rec.id, chapter_order=i, sentence_index=0,
                char_offset=0, audio_ms=0.0, updated_at="2024-01-01T00:00:00+00:00",
            ))
        loaded = lib.get_progress(rec.id)
        assert loaded.chapter_order == 2  # last saved

    def test_no_progress(self, lib):
        assert lib.get_progress(999) is None


class TestBookmarks:
    def test_add_and_list(self, lib):
        rec = lib.add_book(_make_record())
        bm = lib.add_bookmark(Bookmark(
            id=None, book_id=rec.id, chapter_order=1,
            sentence_index=5, label="Passage favori",
            created_at="2024-01-01T00:00:00+00:00",
        ))
        assert bm.id is not None
        bms = lib.get_bookmarks(rec.id)
        assert len(bms) == 1
        assert bms[0].label == "Passage favori"

    def test_remove_bookmark(self, lib):
        rec = lib.add_book(_make_record())
        bm = lib.add_bookmark(Bookmark(
            id=None, book_id=rec.id, chapter_order=0,
            sentence_index=0, label="À supprimer",
            created_at="2024-01-01T00:00:00+00:00",
        ))
        lib.remove_bookmark(bm.id)
        assert lib.get_bookmarks(rec.id) == []
