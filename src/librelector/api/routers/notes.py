"""Notes router — CRUD for user annotations."""
from __future__ import annotations

import dataclasses
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...data.models import Note

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/notes", tags=["notes"])


def _get_session():
    from librelector.api.app import session
    return session


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class NoteCreate(BaseModel):
    book_id: int
    chapter_order: int
    sentence_index: int = 0
    char_start: int = 0
    char_end: int = 0
    highlighted_text: str = ""
    content: str


class NoteUpdate(BaseModel):
    content: str


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/{book_id}")
async def list_notes(book_id: int):
    """Return all notes for a book ordered by position."""
    sess = _get_session()
    if sess.library.get_book(book_id) is None:
        raise HTTPException(status_code=404, detail="Livre introuvable")
    notes = sess.library.get_notes(book_id)
    return {"notes": [dataclasses.asdict(n) for n in notes]}


@router.post("")
async def create_note(body: NoteCreate):
    """Create a new annotation."""
    now = datetime.now(timezone.utc).isoformat()
    sess = _get_session()
    if sess.library.get_book(body.book_id) is None:
        raise HTTPException(status_code=404, detail="Livre introuvable")
    note = Note(
        id=None,
        book_id=body.book_id,
        chapter_order=body.chapter_order,
        sentence_index=body.sentence_index,
        char_start=body.char_start,
        char_end=body.char_end,
        highlighted_text=body.highlighted_text,
        content=body.content,
        created_at=now,
        updated_at=now,
    )
    note = sess.library.add_note(note)
    return dataclasses.asdict(note)


@router.put("/{note_id}")
async def update_note(note_id: int, body: NoteUpdate):
    """Update the text content of an existing note."""
    sess = _get_session()
    sess.library.update_note(note_id, body.content)
    return {"id": note_id, "content": body.content}


@router.delete("/{note_id}")
async def delete_note(note_id: int):
    """Delete a note."""
    sess = _get_session()
    sess.library.remove_note(note_id)
    return {"deleted": note_id}
