from docker.errors import APIError
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from pydantic import BaseModel

from app.security import get_current_user
from app.services.docker_client import get_container_for_service
from app.services.project_manager import load_project


router = APIRouter()

_CONTAINER_ACTIONS: dict[str, str] = {
    "start": "start",
    "stop": "stop",
    "restart": "restart",
    "pause": "pause",
    "unpause": "unpause",
    "kill": "kill",
}


class ActionResponse(BaseModel):
    service: str
    action: str
    status: str
    message: str = ""


def _perform_action(project_id: str, service_name: str, action: str) -> ActionResponse:
    project = load_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projet introuvable")

    if not any(s.name == service_name for s in project.services):
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' introuvable")

    container = get_container_for_service(project_id, service_name)
    if container is None:
        raise HTTPException(
            status_code=404,
            detail=f"Container pour '{service_name}' introuvable (démarré via compose ?)",
        )

    method_name = _CONTAINER_ACTIONS.get(action)
    if method_name is None:
        raise HTTPException(status_code=400, detail=f"Action inconnue : {action}")

    try:
        getattr(container, method_name)()
        container.reload()
        return ActionResponse(service=service_name, action=action, status=container.status)
    except HTTPException:
        raise
    except APIError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/{project_id}/services/{service_name}/start", response_model=ActionResponse)
def start_service(project_id: str, service_name: str, _: dict = Depends(get_current_user)) -> ActionResponse:
    return _perform_action(project_id, service_name, "start")


@router.post("/{project_id}/services/{service_name}/stop", response_model=ActionResponse)
def stop_service(project_id: str, service_name: str, _: dict = Depends(get_current_user)) -> ActionResponse:
    return _perform_action(project_id, service_name, "stop")


@router.post("/{project_id}/services/{service_name}/restart", response_model=ActionResponse)
def restart_service(project_id: str, service_name: str, _: dict = Depends(get_current_user)) -> ActionResponse:
    return _perform_action(project_id, service_name, "restart")


@router.post("/{project_id}/services/{service_name}/pause", response_model=ActionResponse)
def pause_service(project_id: str, service_name: str, _: dict = Depends(get_current_user)) -> ActionResponse:
    return _perform_action(project_id, service_name, "pause")


@router.post("/{project_id}/services/{service_name}/unpause", response_model=ActionResponse)
def unpause_service(project_id: str, service_name: str, _: dict = Depends(get_current_user)) -> ActionResponse:
    return _perform_action(project_id, service_name, "unpause")
