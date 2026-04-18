"""Tests for Note model and Library CRUD."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from librelector.data.library import Library
from librelector.data.models import BookRecord, Note


@pytest.fixture
def library(tmp_path):
    db = tmp_path / "test.db"
    lib = Library(db_path=db)
    yield lib
    lib.close()


@pytest.fixture
def book(library):
    from datetime import datetime, timezone
    record = BookRecord(
        id=None,
        file_path="/fake/book.epub",
        title="Test Book",
        author="Author",
        language="fr",
        identifier="test-id",
        cover_path=None,
        chapter_count=3,
        added_at=datetime.now(timezone.utc).isoformat(),
    )
    return library.add_book(record)


def _make_note(book_id: int, chapter: int = 0, content: str = "Ma note") -> Note:
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    return Note(
        id=None,
        book_id=book_id,
        chapter_order=chapter,
        sentence_index=2,
        char_start=100,
        char_end=150,
        highlighted_text="texte surligné",
        content=content,
        created_at=now,
        updated_at=now,
    )


def test_add_and_get_note(library, book):
    note = library.add_note(_make_note(book.id))
    assert note.id is not None

    notes = library.get_notes(book.id)
    assert len(notes) == 1
    assert notes[0].content == "Ma note"
    assert notes[0].highlighted_text == "texte surligné"


def test_multiple_notes_ordered_by_position(library, book):
    library.add_note(_make_note(book.id, chapter=1, content="Deuxième"))
    library.add_note(_make_note(book.id, chapter=0, content="Première"))

    notes = library.get_notes(book.id)
    assert notes[0].chapter_order == 0
    assert notes[1].chapter_order == 1


def test_update_note(library, book):
    note = library.add_note(_make_note(book.id))
    library.update_note(note.id, "Contenu modifié")

    notes = library.get_notes(book.id)
    assert notes[0].content == "Contenu modifié"


def test_delete_note(library, book):
    note = library.add_note(_make_note(book.id))
    library.remove_note(note.id)
    assert library.get_notes(book.id) == []


def test_notes_cascade_on_book_delete(library, book):
    library.add_note(_make_note(book.id))
    library.remove_book(book.id)
    # notes table should be empty (ON DELETE CASCADE)
    rows = library._conn.execute("SELECT * FROM notes").fetchall()
    assert rows == []
