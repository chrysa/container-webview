from __future__ import annotations

import asyncio
import contextlib
import logging
import typing

from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect

from app.security import security
from app.services.docker_client import docker_client
from app.services.project_manager import project_manager

if typing.TYPE_CHECKING:
    from docker.models.containers import Container

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/{project_id}/services/{service_name}/logs")
async def stream_logs(
    websocket: WebSocket,
    project_id: str,
    service_name: str,
    token: str = Query(...),
    tail: int = Query(100),
) -> None:
    """Stream container logs over a WebSocket connection.

    Authenticates via a `token` query parameter because WebSocket handshakes
    do not carry the Authorization header.
    """
    try:
        security.get_current_user(token)
    except HTTPException:
        await websocket.close(code=4001)
        return

    if not project_manager.load(project_id):
        await websocket.close(code=4004)
        return

    container = docker_client.get_container_for_service(project_id, service_name)
    if container is None:
        await websocket.close(code=4004)
        return

    await websocket.accept()
    await _pipe_logs(websocket, container, tail)


async def _pipe_logs(websocket: WebSocket, container: Container, tail: int) -> None:
    """Forward container log lines to the WebSocket until the client disconnects."""
    try:
        log_stream = container.logs(stream=True, follow=True, tail=tail, timestamps=True)
        for chunk in log_stream:
            line = chunk.decode("utf-8", errors="replace").rstrip("\n")
            await websocket.send_text(line)
            await asyncio.sleep(0)
    except WebSocketDisconnect:
        _logger.debug("WebSocket client disconnected during log stream")
    finally:
        with contextlib.suppress(RuntimeError):
            await websocket.close()