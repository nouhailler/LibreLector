"""SQLite-backed data models."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class BookRecord:
    id: Optional[int]        # None before first INSERT
    file_path: str
    title: str
    author: str
    language: str
    identifier: str
    cover_path: Optional[str]
    chapter_count: int
    added_at: str            # ISO-8601


@dataclass
class ReadingProgress:
    book_id: int
    chapter_order: int
    sentence_index: int
    char_offset: int
    audio_ms: float
    updated_at: str          # ISO-8601


@dataclass
class Bookmark:
    id: Optional[int]
    book_id: int
    chapter_order: int
    sentence_index: int
    label: str
    created_at: str
