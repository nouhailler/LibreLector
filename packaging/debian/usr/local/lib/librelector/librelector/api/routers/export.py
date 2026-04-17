"""Export router — stream MP3 export progress via SSE."""
from __future__ import annotations

import asyncio
import json
import logging
import queue
import threading
from pathlib import Path
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from ...core.exporter import Mp3Exporter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/export", tags=["export"])

_EXPORT_DIR_PRIMARY = Path.home() / "Musique" / "LibreLector"
_EXPORT_DIR_FALLBACK = Path("/tmp/librelector_export")


def _get_session():
    from librelector.api.app import session
    return session


def _resolve_export_dir() -> Path:
    """Return the best available export directory."""
    try:
        _EXPORT_DIR_PRIMARY.mkdir(parents=True, exist_ok=True)
        return _EXPORT_DIR_PRIMARY
    except OSError:
        _EXPORT_DIR_FALLBACK.mkdir(parents=True, exist_ok=True)
        return _EXPORT_DIR_FALLBACK


@router.post("/chapter/{order}")
async def export_chapter(order: int):
    """Export a single chapter to MP3 and stream SSE progress events."""
    sess = _get_session()

    if sess.player is None or sess.player.book is None:
        raise HTTPException(status_code=404, detail="Aucun livre chargé")

    chapter = sess.player.book.chapter_by_order(order)
    if chapter is None:
        raise HTTPException(status_code=404, detail=f"Chapitre {order} introuvable")

    piper_model = sess.settings.get("piper_model", "")
    if not piper_model:
        raise HTTPException(status_code=409, detail="Aucun modèle Piper configuré dans les settings")

    export_dir = _resolve_export_dir()

    async def event_stream() -> AsyncGenerator[str, None]:
        q: queue.Queue = queue.Queue()

        def run_export() -> None:
            try:
                exporter = Mp3Exporter(model_path=piper_model)
                if not exporter.is_available():
                    q.put({"type": "error", "message": "Piper ou ffmpeg non disponible"})
                    return

                mp3_path = exporter.export_chapter(chapter, export_dir)

                if mp3_path:
                    q.put({
                        "type": "progress",
                        "current": 1,
                        "total": 1,
                        "title": chapter.title,
                        "path": str(mp3_path),
                    })
                    q.put({"type": "done", "path": str(mp3_path)})
                else:
                    q.put({"type": "error", "message": "L'export a échoué (fichier vide ou erreur ffmpeg)"})
            except Exception as exc:
                logger.error("Export error: %s", exc)
                q.put({"type": "error", "message": str(exc)})
            finally:
                q.put(None)  # sentinel

        # Run the blocking export in a thread
        thread = threading.Thread(target=run_export, daemon=True)
        thread.start()

        # Poll non-bloquant : vérifie la queue toutes les 500ms sans timeout global
        while True:
            try:
                item = q.get_nowait()
            except queue.Empty:
                await asyncio.sleep(0.5)
                continue

            if item is None:
                break
            yield f"data: {json.dumps(item)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
