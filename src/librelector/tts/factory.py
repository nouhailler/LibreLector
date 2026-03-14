"""Factory to select and instantiate the best available TTS engine."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from .base import TTSEngine
from .piper import PiperEngine
from .speech_dispatcher import SpeechDispatcherEngine

logger = logging.getLogger(__name__)


def create_engine(
    preferred: str = "piper",
    piper_model: Optional[str | Path] = None,
    language: str = "fr",
) -> TTSEngine:
    """
    Return the best available TTS engine.

    Parameters
    ----------
    preferred:
        ``"piper"`` (default) or ``"speech_dispatcher"``.
    piper_model:
        Path to the Piper `.onnx` model.  Required when *preferred* is
        ``"piper"``.
    language:
        BCP-47 language tag used by Speech Dispatcher fallback.
    """
    if preferred == "piper" and piper_model:
        engine = PiperEngine(piper_model)
        if engine.is_available():
            logger.info("Using Piper TTS engine (%s)", piper_model)
            return engine
        logger.warning("Piper not available, falling back to Speech Dispatcher")

    engine = SpeechDispatcherEngine(language=language)
    if engine.is_available():
        logger.info("Using Speech Dispatcher TTS engine")
        return engine

    raise RuntimeError(
        "No TTS engine available.  Install Piper (https://github.com/rhasspy/piper) "
        "or Speech Dispatcher (sudo apt install speech-dispatcher)."
    )
