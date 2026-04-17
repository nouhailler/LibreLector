"""Library router — CRUD for books and folders."""
from __future__ import annotations

import dataclasses
import logging
import shutil
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/library", tags=["library"])

_BOOKS_DIR = Path.home() / ".local" / "share" / "LibreLector" / "books"


def _get_session():
    from librelector.api.app import session
    return session


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class FolderCreate(BaseModel):
    name: str


class FolderRename(BaseModel):
    name: str


class BookFolder(BaseModel):
    folder_id: Optional[int] = None


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("")
@router.get("/")
async def list_library():
    """Return all folders and books."""
    sess = _get_session()
    folders = [dataclasses.asdict(f) for f in sess.library.all_folders()]
    books = [dataclasses.asdict(b) for b in sess.library.all_books()]
    return {"folders": folders, "books": books}


@router.post("/books/upload")
async def upload_book(file: UploadFile = File(...)):
    """Upload an EPUB file and register it in the library."""
    sess = _get_session()
    if not file.filename or not file.filename.lower().endswith(".epub"):
        raise HTTPException(status_code=400, detail="Seuls les fichiers EPUB sont acceptés")

    _BOOKS_DIR.mkdir(parents=True, exist_ok=True)
    dest = _BOOKS_DIR / file.filename

    try:
        with dest.open("wb") as fh:
            shutil.copyfileobj(file.file, fh)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la sauvegarde : {exc}") from exc

    # Initialise player if needed, then open the book to register it
    if sess.player is None:
        try:
            sess.init_player()
        except Exception as exc:
            logger.warning("Impossible d'initialiser le player TTS : %s", exc)

    try:
        import asyncio
        if sess.player is not None:
            book = await asyncio.to_thread(sess.player.open_book, str(dest))
            record = sess.player._book_record  # already saved by open_book
        else:
            # Parse without TTS to register the book
            from librelector.epub import EpubParser
            from librelector.data.models import BookRecord
            from datetime import datetime, timezone
            parser = EpubParser()
            epub = await asyncio.to_thread(parser.parse, dest)
            record = BookRecord(
                id=None,
                file_path=str(dest),
                title=epub.title,
                author=epub.author,
                language=epub.language,
                identifier=epub.identifier,
                cover_path=epub.cover_path,
                chapter_count=epub.chapter_count,
                added_at=datetime.now(timezone.utc).isoformat(),
            )
            record = sess.library.add_book(record)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erreur lors du parsing EPUB : {exc}") from exc

    return dataclasses.asdict(record)


@router.delete("/books/{book_id}")
async def delete_book(book_id: int):
    """Remove a book from the library (DB only, file is kept)."""
    sess = _get_session()
    book = sess.library.get_book(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Livre introuvable")
    sess.library.remove_book(book_id)
    return {"deleted": book_id}


@router.post("/folders")
async def create_folder(body: FolderCreate):
    """Create a new folder."""
    sess = _get_session()
    folder = sess.library.add_folder(body.name)
    return dataclasses.asdict(folder)


@router.put("/folders/{folder_id}")
async def rename_folder(folder_id: int, body: FolderRename):
    """Rename an existing folder."""
    sess = _get_session()
    sess.library.rename_folder(folder_id, body.name)
    return {"id": folder_id, "name": body.name}


@router.delete("/folders/{folder_id}")
async def delete_folder(folder_id: int):
    """Delete a folder (books are unassigned, not deleted)."""
    sess = _get_session()
    sess.library.remove_folder(folder_id)
    return {"deleted": folder_id}


@router.put("/books/{book_id}/folder")
async def move_book_to_folder(book_id: int, body: BookFolder):
    """Assign (or unassign) a book to a folder."""
    sess = _get_session()
    book = sess.library.get_book(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Livre introuvable")
    sess.library.move_book_to_folder(book_id, body.folder_id)
    return {"book_id": book_id, "folder_id": body.folder_id}
