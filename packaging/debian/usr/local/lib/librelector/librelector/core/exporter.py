"""Export EPUB chapters to MP3 via Piper + ffmpeg."""
from __future__ import annotations

import logging
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Callable, Optional

from ..epub.models import EpubBook, EpubChapter

logger = logging.getLogger(__name__)


class Mp3Exporter:
    """
    Synthesise an EpubBook (or a single chapter) to MP3 using Piper + ffmpeg.

    Usage::

        exporter = Mp3Exporter(model_path="~/.local/share/LibreLector/voices/fr_FR-siwis-medium.onnx")
        exporter.export_book(book, output_dir="/tmp/export",
                             progress_cb=lambda cur, total, title: print(f"{cur}/{total} {title}"))
    """

    def __init__(self, model_path: str | Path, speed: float = 1.0):
        self.model_path = Path(model_path).expanduser()
        self.config_path = self.model_path.with_suffix(".onnx.json")
        self.speed = speed

    # ── public API ────────────────────────────────────────────────────────────

    def is_available(self) -> bool:
        piper = shutil.which("piper") or shutil.which("piper-tts")
        ffmpeg = shutil.which("ffmpeg")
        return bool(piper and ffmpeg and self.model_path.exists())

    def export_book(
        self,
        book: EpubBook,
        output_dir: str | Path,
        progress_cb: Optional[Callable[[int, int, str], None]] = None,
        stop_flag: Optional[Callable[[], bool]] = None,
    ) -> list[Path]:
        """Export all chapters of *book* to MP3 files in *output_dir*.

        Parameters
        ----------
        book:        parsed EpubBook
        output_dir:  destination directory (created if needed)
        progress_cb: called with (current, total, chapter_title) after each chapter
        stop_flag:   callable returning True to abort the export early

        Returns
        -------
        List of generated MP3 paths.
        """
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        generated: list[Path] = []
        total = len(book.chapters)

        for idx, chapter in enumerate(book.chapters):
            if stop_flag and stop_flag():
                logger.info("Export aborted by user at chapter %d", idx)
                break
            mp3_path = self.export_chapter(chapter, out)
            if mp3_path:
                generated.append(mp3_path)
            if progress_cb:
                progress_cb(idx + 1, total, chapter.title)

        return generated

    def export_chapter(self, chapter: EpubChapter, output_dir: Path) -> Optional[Path]:
        """Synthesise one chapter and write an MP3 next to the others."""
        piper_bin = shutil.which("piper") or shutil.which("piper-tts") or "piper"
        safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in chapter.title)
        mp3_path = output_dir / f"{chapter.order:03d}_{safe_title}.mp3"

        cmd_piper = [
            piper_bin,
            "--model", str(self.model_path),
            "--output_raw",
            "--length_scale", f"{1.0 / self.speed:.2f}",
        ]
        if self.config_path.exists():
            cmd_piper += ["--config", str(self.config_path)]

        cmd_ffmpeg = [
            "ffmpeg", "-y",
            "-f", "s16le", "-ar", "22050", "-ac", "1",
            "-i", "pipe:0",
            "-codec:a", "libmp3lame", "-q:a", "4",
            str(mp3_path),
        ]

        try:
            piper_proc = subprocess.Popen(
                cmd_piper,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
            )
            ffmpeg_proc = subprocess.Popen(
                cmd_ffmpeg,
                stdin=piper_proc.stdout,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            piper_proc.stdout.close()
            piper_proc.stdin.write(chapter.plain_text.encode("utf-8"))
            piper_proc.stdin.close()
            piper_proc.wait()
            ffmpeg_proc.wait()

            if mp3_path.exists() and mp3_path.stat().st_size > 0:
                logger.info("Exported: %s", mp3_path)
                return mp3_path
            else:
                logger.error("ffmpeg produced empty file for chapter %s", chapter.title)
                return None

        except Exception as exc:
            logger.error("Export failed for chapter %s: %s", chapter.title, exc)
            return None
