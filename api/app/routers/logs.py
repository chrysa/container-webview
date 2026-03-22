import asyncio

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.security import security
from app.services.docker_client import docker_client
from app.services.project_manager import project_manager

router = APIRouter()


@router.websocket("/{project_id}/services/{service_name}/logs")
async def stream_logs(
    websocket: WebSocket,
    project_id: str,
    service_name: str,
    token: str = Query(...),
    tail: int = Query(100),
) -> None:
    # Auth via query param (WebSocket does not support Authorization headers)
    try:
        security.get_current_user(token)  # raises HTTPException if invalid
    except Exception:
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
    try:
        log_stream = container.logs(stream=True, follow=True, tail=tail, timestamps=True)
        for chunk in log_stream:
            line = chunk.decode("utf-8", errors="replace").rstrip("\n")
            await websocket.send_text(line)
            await asyncio.sleep(0)
    except WebSocketDisconnect:
        pass
    except Exception as exc:
        try:
            await websocket.send_text(f"[ERROR] {exc}")
        except Exception:
            pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
