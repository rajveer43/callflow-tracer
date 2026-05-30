"""Live WebSocket dashboard server.

Observer Pattern:
  - DashboardServer is the Subject (broadcasts snapshots)
  - Each connected WebSocket client is an Observer

The server pushes a fresh JSON snapshot every `interval_s` seconds.
Clients can also send a JSON `{"cmd": "snapshot"}` to get an on-demand push.

Dependencies: websockets (pip install websockets). Falls back gracefully
if not installed — server.start() raises ImportError with a helpful message.

Usage::

    from callflow_tracer.dashboard import DashboardServer, DashboardRenderer

    renderer = DashboardRenderer(call_graph=g, llm_registry=r, sampler=s)
    server = DashboardServer(renderer, port=7474, interval_s=2.0)
    server.start()          # starts asyncio loop in background thread
    ...
    server.stop()
"""

from __future__ import annotations

import asyncio
import json
import logging
import threading
from typing import Optional, Set

from .renderer import DashboardRenderer

logger = logging.getLogger(__name__)


class DashboardServer:
    """Async WebSocket server that broadcasts graph snapshots to connected clients."""

    def __init__(
        self,
        renderer: DashboardRenderer,
        host: str = "localhost",
        port: int = 7474,
        interval_s: float = 2.0,
    ) -> None:
        self._renderer = renderer
        self._host = host
        self._port = port
        self._interval = interval_s
        self._clients: Set[Any] = set()  # websocket objects
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._server_task: Optional[asyncio.Task] = None
        self._running = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start the server in a background daemon thread."""
        try:
            import websockets  # noqa: F401
        except ImportError as exc:
            raise ImportError(
                "websockets is required for the dashboard. "
                "Install it with: pip install websockets"
            ) from exc

        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(
            target=self._run_loop, daemon=True, name="cf-dashboard"
        )
        self._thread.start()
        logger.info("Dashboard server started at ws://%s:%s", self._host, self._port)

    def stop(self) -> None:
        if not self._running:
            return
        self._running = False
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread:
            self._thread.join(timeout=3.0)

    def url(self) -> str:
        return f"ws://{self._host}:{self._port}"

    # ------------------------------------------------------------------
    # Internal asyncio runner
    # ------------------------------------------------------------------

    def _run_loop(self) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._serve())
        finally:
            self._loop.close()

    async def _serve(self) -> None:
        import websockets

        async with websockets.serve(self._handler, self._host, self._port):
            # Broadcast loop
            while self._running:
                await self._broadcast(self._renderer.snapshot_json())
                await asyncio.sleep(self._interval)

    async def _handler(self, websocket: Any, path: str = "/") -> None:
        self._clients.add(websocket)
        logger.debug("Client connected: %s (total: %d)", websocket.remote_address, len(self._clients))
        try:
            # Send immediate snapshot on connect
            await websocket.send(self._renderer.snapshot_json())
            async for message in websocket:
                try:
                    cmd = json.loads(message)
                    if cmd.get("cmd") == "snapshot":
                        await websocket.send(self._renderer.snapshot_json())
                except (json.JSONDecodeError, Exception):
                    pass
        except Exception:
            pass
        finally:
            self._clients.discard(websocket)

    async def _broadcast(self, message: str) -> None:
        if not self._clients:
            return
        dead = set()
        for ws in list(self._clients):
            try:
                await ws.send(message)
            except Exception:
                dead.add(ws)
        self._clients -= dead


# Type alias for websocket — resolved at runtime
from typing import Any  # noqa: E402
