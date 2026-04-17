"""FastAPI application entry point."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .session import AppSession
from .routers import library, reader, player, settings, export

logger = logging.getLogger(__name__)

# Module-level singleton — imported by all routers via lazy import
session: AppSession  # assigned inside lifespan before requests are served

def _locate_ui_dist() -> Path:
    """Search parent directories for the built React UI (works both in-source and installed)."""
    here = Path(__file__).resolve().parent
    for _ in range(6):
        candidate = here / "ui" / "dist"
        if candidate.exists():
            return candidate
        here = here.parent
    # Fallback: expected installed location (/usr/local/lib/librelector/ui/dist)
    return Path(__file__).resolve().parent.parent.parent / "ui" / "dist"

_UI_DIST = _locate_ui_dist()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise the session on startup, clean up on shutdown."""
    global session
    logger.info("LibreLector API starting…")
    session = AppSession()
    yield
    logger.info("LibreLector API shutting down…")
    session.library.close()


app = FastAPI(title="LibreLector API", version="1.0.0", lifespan=lifespan)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(library.router)
app.include_router(reader.router)
app.include_router(player.router)
app.include_router(settings.router)
app.include_router(export.router)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/api/health")
async def health():
    return {"status": "ok"}


# ── WebSocket ─────────────────────────────────────────────────────────────────
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await session.ws_manager.connect(ws)
    try:
        while True:
            # Keep the connection alive; we only push from server to client
            await ws.receive_text()
    except WebSocketDisconnect:
        session.ws_manager.disconnect(ws)
    except Exception:
        session.ws_manager.disconnect(ws)


# ── Static files (React UI) ───────────────────────────────────────────────────
# Mount static assets directory for JS/CSS/images.
# A catch-all GET route handles SPA deep links by returning index.html.
if _UI_DIST.exists():
    logger.info("Serving React UI from %s", _UI_DIST)

    # Serve individual static assets (JS, CSS, images, etc.)
    app.mount("/assets", StaticFiles(directory=str(_UI_DIST / "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str):
        """Serve a static file if it exists, otherwise return index.html."""
        candidate = _UI_DIST / full_path
        if candidate.exists() and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(_UI_DIST / "index.html")
