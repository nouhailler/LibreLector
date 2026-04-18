"""Document format detection and factory.

Usage::

    from librelector.document import load_document
    book = load_document("/path/to/file.pdf")  # returns EpubBook
"""
from __future__ import annotations

import logging
from pathlib import Path

from ..epub.models import EpubBook
from .base import DocumentParser

logger = logging.getLogger(__name__)

# Map of lower-case file extension → parser class (imported lazily)
_FORMAT_MAP: dict[str, str] = {
    ".epub": "epub_doc.EpubDocumentParser",
    ".pdf":  "pdf_doc.PdfDocumentParser",
    ".txt":  "txt_doc.TxtDocumentParser",
    ".fb2":  "fb2_doc.Fb2DocumentParser",
}

# Magic-byte signatures for format detection without relying on extension
_MAGIC: list[tuple[bytes, str]] = [
    (b"PK\x03\x04", ".epub"),   # ZIP (EPUB is a ZIP)
    (b"%PDF",       ".pdf"),
    (b"<?xml",      ".fb2"),
]

SUPPORTED_EXTENSIONS = set(_FORMAT_MAP.keys())


def _detect_format(path: Path) -> str:
    """Return the canonical extension for *path*, using magic bytes as fallback."""
    ext = path.suffix.lower()
    if ext in _FORMAT_MAP:
        return ext

    # Try magic bytes
    try:
        with path.open("rb") as fh:
            header = fh.read(16)
        for magic, detected_ext in _MAGIC:
            if header.startswith(magic):
                return detected_ext
    except OSError:
        pass

    raise ValueError(
        f"Format non reconnu pour «{path.name}». "
        f"Extensions supportées : {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
    )


def _get_parser(ext: str) -> DocumentParser:
    """Instantiate the parser registered for *ext*."""
    module_class = _FORMAT_MAP[ext]
    module_name, class_name = module_class.rsplit(".", 1)
    # Lazy import so optional dependencies (PyMuPDF, …) are only required
    # when the corresponding format is actually used.
    import importlib
    module = importlib.import_module(f"librelector.document.{module_name}")
    cls = getattr(module, class_name)
    return cls()


def load_document(path: str | Path) -> EpubBook:
    """Detect the format of *path* and parse it into an :class:`EpubBook`.

    Parameters
    ----------
    path:
        Path to the document (EPUB, PDF, TXT, or FB2).

    Returns
    -------
    EpubBook
        A fully populated book object usable by :class:`~librelector.core.player.Player`.

    Raises
    ------
    ValueError
        If the format is not recognised or the file cannot be parsed.
    ImportError
        If a required optional dependency (e.g. PyMuPDF) is missing.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {path}")

    ext = _detect_format(path)
    logger.info("Loading %s document: %s", ext, path)
    parser = _get_parser(ext)
    return parser.parse(path)
