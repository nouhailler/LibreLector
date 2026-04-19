"""Bookmarks router — CRUD pour les marque-pages."""
from __future__ import annotations

import dataclasses
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...data.models import Bookmark

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/bookmarks", tags=["bookmarks"])


def _get_session():
    from librelector.api.app import session
    return session


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class BookmarkCreate(BaseModel):
    book_id: int
    chapter_order: int
    sentence_index: int = 0
    label: str = ""


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/{book_id}")
async def list_bookmarks(book_id: int):
    """Retourne tous les marque-pages d'un livre, triés par position."""
    sess = _get_session()
    if sess.library.get_book(book_id) is None:
        raise HTTPException(status_code=404, detail="Livre introuvable")
    bms = sess.library.get_bookmarks(book_id)
    return {"bookmarks": [dataclasses.asdict(b) for b in bms]}


@router.post("")
async def create_bookmark(body: BookmarkCreate):
    """Crée un nouveau marque-page."""
    sess = _get_session()
    if sess.library.get_book(body.book_id) is None:
        raise HTTPException(status_code=404, detail="Livre introuvable")
    now = datetime.now(timezone.utc).isoformat()
    bm = Bookmark(
        id=None,
        book_id=body.book_id,
        chapter_order=body.chapter_order,
        sentence_index=body.sentence_index,
        label=body.label,
        created_at=now,
    )
    bm = sess.library.add_bookmark(bm)
    return dataclasses.asdict(bm)


@router.delete("/{bookmark_id}")
async def delete_bookmark(bookmark_id: int):
    """Supprime un marque-page."""
    sess = _get_session()
    sess.library.remove_bookmark(bookmark_id)
    return {"deleted": bookmark_id}
