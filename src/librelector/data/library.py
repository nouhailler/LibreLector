"""SQLite library manager for LibreLector.

Schema
------
books            – one row per EPUB file
reading_progress – latest reading position per book
bookmarks        – user-created bookmarks
folders          – user-defined organizational folders
"""
from __future__ import annotations

import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .models import BookRecord, Bookmark, Folder, Note, ReadingProgress

logger = logging.getLogger(__name__)

_SCHEMA = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS books (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path     TEXT    NOT NULL UNIQUE,
    title         TEXT    NOT NULL,
    author        TEXT    NOT NULL DEFAULT '',
    language      TEXT    NOT NULL DEFAULT 'fr',
    identifier    TEXT    NOT NULL DEFAULT '',
    cover_path    TEXT,
    chapter_count INTEGER NOT NULL DEFAULT 0,
    added_at      TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS reading_progress (
    book_id       INTEGER PRIMARY KEY REFERENCES books(id) ON DELETE CASCADE,
    chapter_order INTEGER NOT NULL DEFAULT 0,
    sentence_index INTEGER NOT NULL DEFAULT 0,
    char_offset   INTEGER NOT NULL DEFAULT 0,
    audio_ms      REAL    NOT NULL DEFAULT 0.0,
    updated_at    TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS bookmarks (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id       INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    chapter_order INTEGER NOT NULL,
    sentence_index INTEGER NOT NULL DEFAULT 0,
    label         TEXT    NOT NULL DEFAULT '',
    created_at    TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS folders (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL,
    created_at TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS notes (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id          INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    chapter_order    INTEGER NOT NULL,
    sentence_index   INTEGER NOT NULL DEFAULT 0,
    char_start       INTEGER NOT NULL DEFAULT 0,
    char_end         INTEGER NOT NULL DEFAULT 0,
    highlighted_text TEXT    NOT NULL DEFAULT '',
    content          TEXT    NOT NULL DEFAULT '',
    type             TEXT    NOT NULL DEFAULT 'note',
    created_at       TEXT    NOT NULL,
    updated_at       TEXT    NOT NULL
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Library:
    """Manages the LibreLector SQLite database."""

    DEFAULT_DIR = Path.home() / ".local" / "share" / "LibreLector"

    def __init__(self, db_path: Optional[str | Path] = None) -> None:
        if db_path is None:
            self.DEFAULT_DIR.mkdir(parents=True, exist_ok=True)
            db_path = self.DEFAULT_DIR / "metadata.db"
        self._db_path = Path(db_path)
        self._conn = sqlite3.connect(str(self._db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._conn.executescript(_SCHEMA)
        self._conn.commit()
        self._apply_migrations()
        logger.info("Library opened: %s", self._db_path)

    def _apply_migrations(self) -> None:
        cols = {row[1] for row in self._conn.execute("PRAGMA table_info(books)").fetchall()}
        if "folder_id" not in cols:
            self._conn.execute(
                "ALTER TABLE books ADD COLUMN folder_id INTEGER REFERENCES folders(id) ON DELETE SET NULL"
            )
            self._conn.commit()
            logger.info("Migration : colonne folder_id ajoutée à books")

        note_cols = {row[1] for row in self._conn.execute("PRAGMA table_info(notes)").fetchall()}
        if "type" not in note_cols:
            self._conn.execute(
                "ALTER TABLE notes ADD COLUMN type TEXT NOT NULL DEFAULT 'note'"
            )
            self._conn.commit()
            logger.info("Migration : colonne type ajoutée à notes")

    def close(self) -> None:
        self._conn.close()

    # ── books ─────────────────────────────────────────────────────────────────

    def add_book(self, record: BookRecord) -> BookRecord:
        cur = self._conn.execute(
            """INSERT INTO books
               (file_path, title, author, language, identifier,
                cover_path, chapter_count, added_at)
               VALUES (?,?,?,?,?,?,?,?)
               ON CONFLICT(file_path) DO UPDATE SET
                   title=excluded.title,
                   author=excluded.author,
                   cover_path=excluded.cover_path,
                   chapter_count=excluded.chapter_count
               RETURNING id""",
            (
                record.file_path, record.title, record.author,
                record.language, record.identifier, record.cover_path,
                record.chapter_count, record.added_at or _now(),
            ),
        )
        row = cur.fetchone()
        self._conn.commit()
        record.id = row["id"]
        return record

    def all_books(self) -> list[BookRecord]:
        rows = self._conn.execute(
            "SELECT * FROM books ORDER BY added_at DESC"
        ).fetchall()
        return [self._row_to_book(r) for r in rows]

    def get_book(self, book_id: int) -> Optional[BookRecord]:
        row = self._conn.execute(
            "SELECT * FROM books WHERE id=?", (book_id,)
        ).fetchone()
        return self._row_to_book(row) if row else None

    def get_book_by_path(self, path: str) -> Optional[BookRecord]:
        row = self._conn.execute(
            "SELECT * FROM books WHERE file_path=?", (path,)
        ).fetchone()
        return self._row_to_book(row) if row else None

    def remove_book(self, book_id: int) -> None:
        self._conn.execute("DELETE FROM books WHERE id=?", (book_id,))
        self._conn.commit()

    def move_book_to_folder(self, book_id: int, folder_id: Optional[int]) -> None:
        self._conn.execute(
            "UPDATE books SET folder_id=? WHERE id=?", (folder_id, book_id)
        )
        self._conn.commit()

    # ── folders ───────────────────────────────────────────────────────────────

    def add_folder(self, name: str) -> Folder:
        cur = self._conn.execute(
            "INSERT INTO folders (name, created_at) VALUES (?,?) RETURNING id",
            (name, _now()),
        )
        folder_id = cur.fetchone()["id"]
        self._conn.commit()
        return Folder(id=folder_id, name=name, created_at=_now())

    def all_folders(self) -> list[Folder]:
        rows = self._conn.execute(
            "SELECT * FROM folders ORDER BY name COLLATE NOCASE"
        ).fetchall()
        return [Folder(id=r["id"], name=r["name"], created_at=r["created_at"]) for r in rows]

    def rename_folder(self, folder_id: int, new_name: str) -> None:
        self._conn.execute(
            "UPDATE folders SET name=? WHERE id=?", (new_name, folder_id)
        )
        self._conn.commit()

    def remove_folder(self, folder_id: int) -> None:
        # Détacher les livres du dossier (défense si FK désactivées)
        self._conn.execute(
            "UPDATE books SET folder_id=NULL WHERE folder_id=?", (folder_id,)
        )
        self._conn.execute("DELETE FROM folders WHERE id=?", (folder_id,))
        self._conn.commit()

    # ── reading progress ──────────────────────────────────────────────────────

    def save_progress(self, progress: ReadingProgress) -> None:
        self._conn.execute(
            """INSERT INTO reading_progress
               (book_id, chapter_order, sentence_index, char_offset, audio_ms, updated_at)
               VALUES (?,?,?,?,?,?)
               ON CONFLICT(book_id) DO UPDATE SET
                   chapter_order=excluded.chapter_order,
                   sentence_index=excluded.sentence_index,
                   char_offset=excluded.char_offset,
                   audio_ms=excluded.audio_ms,
                   updated_at=excluded.updated_at""",
            (
                progress.book_id, progress.chapter_order,
                progress.sentence_index, progress.char_offset,
                progress.audio_ms, progress.updated_at or _now(),
            ),
        )
        self._conn.commit()

    def get_progress(self, book_id: int) -> Optional[ReadingProgress]:
        row = self._conn.execute(
            "SELECT * FROM reading_progress WHERE book_id=?", (book_id,)
        ).fetchone()
        if not row:
            return None
        return ReadingProgress(
            book_id=row["book_id"],
            chapter_order=row["chapter_order"],
            sentence_index=row["sentence_index"],
            char_offset=row["char_offset"],
            audio_ms=row["audio_ms"],
            updated_at=row["updated_at"],
        )

    # ── bookmarks ─────────────────────────────────────────────────────────────

    def add_bookmark(self, bm: Bookmark) -> Bookmark:
        cur = self._conn.execute(
            """INSERT INTO bookmarks
               (book_id, chapter_order, sentence_index, label, created_at)
               VALUES (?,?,?,?,?) RETURNING id""",
            (bm.book_id, bm.chapter_order, bm.sentence_index,
             bm.label, bm.created_at or _now()),
        )
        bm.id = cur.fetchone()["id"]
        self._conn.commit()
        return bm

    def get_bookmarks(self, book_id: int) -> list[Bookmark]:
        rows = self._conn.execute(
            "SELECT * FROM bookmarks WHERE book_id=? ORDER BY chapter_order, sentence_index",
            (book_id,),
        ).fetchall()
        return [
            Bookmark(
                id=r["id"], book_id=r["book_id"],
                chapter_order=r["chapter_order"],
                sentence_index=r["sentence_index"],
                label=r["label"], created_at=r["created_at"],
            )
            for r in rows
        ]

    def remove_bookmark(self, bookmark_id: int) -> None:
        self._conn.execute("DELETE FROM bookmarks WHERE id=?", (bookmark_id,))
        self._conn.commit()

    # ── notes ─────────────────────────────────────────────────────────────────

    def add_note(self, note: Note) -> Note:
        now = _now()
        cur = self._conn.execute(
            """INSERT INTO notes
               (book_id, chapter_order, sentence_index, char_start, char_end,
                highlighted_text, content, type, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?) RETURNING id""",
            (
                note.book_id, note.chapter_order, note.sentence_index,
                note.char_start, note.char_end, note.highlighted_text,
                note.content, note.type, note.created_at or now, note.updated_at or now,
            ),
        )
        note.id = cur.fetchone()["id"]
        self._conn.commit()
        return note

    def get_notes(self, book_id: int) -> list[Note]:
        rows = self._conn.execute(
            "SELECT * FROM notes WHERE book_id=? ORDER BY chapter_order, char_start",
            (book_id,),
        ).fetchall()
        return [self._row_to_note(r) for r in rows]

    def update_note(self, note_id: int, content: str) -> None:
        self._conn.execute(
            "UPDATE notes SET content=?, updated_at=? WHERE id=?",
            (content, _now(), note_id),
        )
        self._conn.commit()

    def remove_note(self, note_id: int) -> None:
        self._conn.execute("DELETE FROM notes WHERE id=?", (note_id,))
        self._conn.commit()

    # ── helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _row_to_note(row: sqlite3.Row) -> Note:
        return Note(
            id=row["id"],
            book_id=row["book_id"],
            chapter_order=row["chapter_order"],
            sentence_index=row["sentence_index"],
            char_start=row["char_start"],
            char_end=row["char_end"],
            highlighted_text=row["highlighted_text"],
            content=row["content"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            type=row["type"] if "type" in row.keys() else "note",
        )

    @staticmethod
    def _row_to_book(row: sqlite3.Row) -> BookRecord:
        return BookRecord(
            id=row["id"],
            file_path=row["file_path"],
            title=row["title"],
            author=row["author"],
            language=row["language"],
            identifier=row["identifier"],
            cover_path=row["cover_path"],
            chapter_count=row["chapter_count"],
            added_at=row["added_at"],
            folder_id=row["folder_id"],
        )
