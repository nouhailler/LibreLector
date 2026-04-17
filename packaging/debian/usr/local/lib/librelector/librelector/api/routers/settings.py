"""Settings router — read/write application settings and voice list."""
from __future__ import annotations

import logging

from fastapi import APIRouter

router = APIRouter(prefix="/api/settings", tags=["settings"])

logger = logging.getLogger(__name__)


def _get_session():
    from librelector.api.app import session
    return session


@router.get("/")
async def get_settings():
    """Return current settings dict."""
    return _get_session().settings


@router.put("/")
async def update_settings(data: dict):
    """Persist new settings and reinitialise the TTS engine."""
    sess = _get_session()
    sess.save_settings(data)
    return sess.settings


@router.get("/voices")
async def list_voices():
    """Return available Piper voice models."""
    return {"voices": _get_session().list_voices()}
