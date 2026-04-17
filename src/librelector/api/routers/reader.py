"""Reader router — open books, query chapters, reading state."""
from __future__ import annotations

import asyncio
import dataclasses
import logging

from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reader", tags=["reader"])


def _get_session():
    from librelector.api.app import session
    return session


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/open/{book_id}")
async def open_book(book_id: int):
    """Open a book by its library ID and return metadata + progress."""
    sess = _get_session()

    book_record = sess.library.get_book(book_id)
    if book_record is None:
        raise HTTPException(status_code=404, detail="Livre introuvable")

    if sess.player is None:
        try:
            sess.init_player()
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Impossible d'initialiser le TTS : {exc}") from exc

    try:
        epub = await asyncio.to_thread(sess.player.open_book, book_record.file_path)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erreur ouverture EPUB : {exc}") from exc

    progress = sess.library.get_progress(book_record.id)
    progress_data = None
    if progress:
        progress_data = {
            "chapter_order": progress.chapter_order,
            "sentence_index": progress.sentence_index,
        }

    chapters = [
        {
            "order": ch.order,
            "title": ch.title,
            "sentence_count": len(ch.sentences),
        }
        for ch in epub.chapters
    ]

    # Re-fetch record (open_book may have updated cover/chapter_count)
    updated_record = sess.library.get_book(book_record.id) or book_record

    return {
        "book": {
            "id": updated_record.id,
            "title": updated_record.title,
            "author": updated_record.author,
            "language": updated_record.language,
            "chapter_count": updated_record.chapter_count,
            "cover_path": updated_record.cover_path,
        },
        "chapters": chapters,
        "progress": progress_data,
    }


@router.get("/chapter/{order}")
async def get_chapter(order: int):
    """Return chapter content (sentences) by spine order."""
    sess = _get_session()

    if sess.player is None or sess.player.book is None:
        raise HTTPException(status_code=404, detail="Aucun livre chargé")

    chapter = sess.player.book.chapter_by_order(order)
    if chapter is None:
        raise HTTPException(status_code=404, detail=f"Chapitre {order} introuvable")

    sentences = [
        {
            "text": seg.text,
            "index": seg.index,
            "char_start": seg.char_start,
            "char_end": seg.char_end,
        }
        for seg in chapter.sentences
    ]

    return {
        "order": chapter.order,
        "title": chapter.title,
        "sentences": sentences,
    }


@router.get("/state")
async def get_state():
    """Return current reader state."""
    sess = _get_session()

    if sess.player is None:
        return {
            "book_id": None,
            "chapter_order": 0,
            "sentence_index": 0,
            "player_state": "idle",
        }

    book_id = sess.player._book_record.id if sess.player._book_record else None
    return {
        "book_id": book_id,
        "chapter_order": sess.player._chapter_order,
        "sentence_index": sess.player.current_sentence_index,
        "player_state": sess.player.state.name.lower(),
    }
