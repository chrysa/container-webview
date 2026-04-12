import asyncio
import contextlib

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Query
from fastapi import WebSocket
from fastapi import WebSocketDisconnect

from app.security import verify_token
from app.services.docker_client import get_container_for_service
from app.services.project_manager import load_project


router = APIRouter()


@router.websocket("/{project_id}/services/{service_name}/logs")
async def stream_logs(
    websocket: WebSocket,
    project_id: str,
    service_name: str,
    token: str = Query(...),
    tail: int = Query(100),
) -> None:
    # Auth via query param (WebSocket ne supporte pas les headers Authorization)
    try:
        verify_token(token)
    except HTTPException:
        await websocket.close(code=4001)
        return

    project = load_project(project_id)
    if not project:
        await websocket.close(code=4004)
        return

    container = get_container_for_service(project_id, service_name)
    if container is None:
        await websocket.close(code=4004)
        return

    await websocket.accept()
    try:
        log_stream = container.logs(stream=True, follow=True, tail=tail, timestamps=True)
        for chunk in log_stream:
            line = chunk.decode("utf-8", errors="replace").rstrip("\n")
            await websocket.send_text(line)
            await asyncio.sleep(0)  # yield control
    except WebSocketDisconnect:
        pass
    except Exception as exc:  # noqa: BLE001 — unknown errors during log streaming
        with contextlib.suppress(Exception):  # noqa: BLE001
            await websocket.send_text(f"[ERROR] {exc!s}")
    finally:
        with contextlib.suppress(Exception):  # noqa: BLE001
            await websocket.close()
