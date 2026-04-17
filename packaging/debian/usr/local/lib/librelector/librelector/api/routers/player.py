"""Player router — playback controls."""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/player", tags=["player"])

_NO_BOOK = HTTPException(status_code=409, detail="Aucun livre chargé")


def _get_session():
    from librelector.api.app import session
    return session


def _require_player():
    sess = _get_session()
    if sess.player is None:
        raise _NO_BOOK
    return sess.player


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class SpeedBody(BaseModel):
    speed: float


class VolumeBody(BaseModel):
    volume: float


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/play")
async def play():
    player = _require_player()
    try:
        player.play()
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {"status": "playing"}


@router.post("/pause")
async def pause():
    player = _require_player()
    player.pause()
    return {"status": "paused"}


@router.post("/stop")
async def stop():
    player = _require_player()
    player.stop()
    return {"status": "stopped"}


@router.post("/next")
async def next_chapter():
    player = _require_player()
    advanced = player.next_chapter()
    return {"advanced": advanced}


@router.post("/prev")
async def prev_chapter():
    player = _require_player()
    advanced = player.prev_chapter()
    return {"advanced": advanced}


@router.post("/chapter/{order}")
async def go_to_chapter(order: int):
    player = _require_player()
    player.go_to_chapter(order)
    return {"chapter_order": order}


@router.post("/sentence/{idx}")
async def go_to_sentence(idx: int):
    player = _require_player()
    player.go_to_sentence(idx)
    return {"sentence_index": idx}


@router.put("/speed")
async def set_speed(body: SpeedBody):
    player = _require_player()
    player.set_speed(body.speed)
    return {"speed": body.speed}


@router.put("/volume")
async def set_volume(body: VolumeBody):
    player = _require_player()
    player.set_volume(body.volume)
    return {"volume": body.volume}
