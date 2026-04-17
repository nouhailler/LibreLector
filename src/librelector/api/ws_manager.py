"""WebSocket connection manager with thread-safe broadcast."""
from __future__ import annotations

import asyncio
import logging
from typing import Optional

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages active WebSocket connections and broadcasts messages.

    ``broadcast`` is safe to call from any thread (e.g. TTS callbacks).
    It captures the asyncio event loop on first use and dispatches coroutines
    via ``run_coroutine_threadsafe``.
    """

    def __init__(self) -> None:
        self._connections: list[WebSocket] = []
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._connections.append(ws)
        # Capture the running loop so broadcast() can use it from threads
        if self._loop is None:
            self._loop = asyncio.get_event_loop()
        logger.debug("WebSocket connected (%d total)", len(self._connections))

    def disconnect(self, ws: WebSocket) -> None:
        if ws in self._connections:
            self._connections.remove(ws)
        logger.debug("WebSocket disconnected (%d remaining)", len(self._connections))

    def broadcast(self, data: dict) -> None:
        """Send *data* to all connected clients.

        May be called from any thread.  Uses ``run_coroutine_threadsafe`` when
        called from outside the asyncio thread.
        """
        if not self._connections:
            return

        # Lazily grab the running loop if not yet captured
        loop = self._loop
        if loop is None:
            try:
                loop = asyncio.get_event_loop()
                self._loop = loop
            except RuntimeError:
                logger.warning("broadcast() called but no event loop available")
                return

        try:
            # Are we already in the event loop thread?
            running = asyncio.get_running_loop()
        except RuntimeError:
            running = None

        if running is not None and running is loop:
            # Already in the event loop — schedule as a task directly
            asyncio.ensure_future(self._send_all(data), loop=loop)
        else:
            # Called from a background thread
            asyncio.run_coroutine_threadsafe(self._send_all(data), loop)

    async def _send_all(self, data: dict) -> None:
        dead: list[WebSocket] = []
        for ws in list(self._connections):
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)
