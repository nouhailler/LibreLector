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
    if preferred == "piper":
        if not piper_model:
            logger.warning("Piper sélectionné mais piper_model non défini dans settings.json")
        else:
            import shutil
            piper_bin = shutil.which("piper") or shutil.which("piper-tts")
            from pathlib import Path
            model_exists = Path(piper_model).exists()
            if not piper_bin:
                logger.warning("Binaire piper introuvable dans PATH (%s)", __import__('os').environ.get('PATH', ''))
            if not model_exists:
                logger.warning("Modèle Piper introuvable : %s", piper_model)
            engine = PiperEngine(piper_model)
            if engine.is_available():
                logger.info("Using Piper TTS engine (%s)", piper_model)
                return engine
            logger.warning("Piper non disponible (binaire=%s, modèle=%s), fallback Speech Dispatcher", piper_bin, model_exists)

    engine = SpeechDispatcherEngine(language=language)
    if engine.is_available():
        logger.info("Using Speech Dispatcher TTS engine")
        return engine

    raise RuntimeError(
        "No TTS engine available.  Install Piper (https://github.com/rhasspy/piper) "
        "or Speech Dispatcher (sudo apt install speech-dispatcher)."
    )
