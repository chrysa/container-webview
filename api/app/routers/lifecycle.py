from docker.errors import APIError
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from pydantic import BaseModel

from app import demo
from app.config import settings
from app.security import get_current_user
from app.services.docker_client import get_container_for_service
from app.services.project_manager import load_project


router = APIRouter()

_ACTION_RESPONSES: dict[int | str, dict] = {
    400: {"description": "Unknown or unsupported action"},
    404: {"description": "Project, service or container not found"},
    500: {"description": "Docker API error"},
}

_CONTAINER_ACTIONS: dict[str, str] = {
    "start": "start",
    "stop": "stop",
    "restart": "restart",
    "pause": "pause",
    "unpause": "unpause",
    "kill": "kill",
}

# Container status reflected back after a successful action, used in demo mode
# where no real Docker call is made.
_DEMO_ACTION_RESULT: dict[str, str] = {
    "start": "running",
    "restart": "running",
    "unpause": "running",
    "stop": "exited",
    "kill": "exited",
    "pause": "paused",
}


class ActionResponse(BaseModel):
    service: str
    action: str
    status: str
    message: str = ""


def _perform_demo_action(project_id: str, service_name: str, action: str) -> ActionResponse:
    demo_project = demo.load_project(project_id)
    if not demo_project:
        raise HTTPException(status_code=404, detail="Projet introuvable")
    if not any(s["name"] == service_name for s in demo_project["services"]):
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' introuvable")
    if action not in _CONTAINER_ACTIONS:
        raise HTTPException(status_code=400, detail=f"Action inconnue : {action}")
    return ActionResponse(
        service=service_name,
        action=action,
        status=_DEMO_ACTION_RESULT.get(action, "running"),
        message="Demo mode — no real container was changed.",
    )


def _perform_action(project_id: str, service_name: str, action: str) -> ActionResponse:
    if settings.demo_mode:
        return _perform_demo_action(project_id, service_name, action)

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


@router.post("/{project_id}/services/{service_name}/start", response_model=ActionResponse, responses=_ACTION_RESPONSES)
def start_service(project_id: str, service_name: str, _: dict = Depends(get_current_user)) -> ActionResponse:
    return _perform_action(project_id, service_name, "start")


@router.post("/{project_id}/services/{service_name}/stop", response_model=ActionResponse, responses=_ACTION_RESPONSES)
def stop_service(project_id: str, service_name: str, _: dict = Depends(get_current_user)) -> ActionResponse:
    return _perform_action(project_id, service_name, "stop")


@router.post(
    "/{project_id}/services/{service_name}/restart", response_model=ActionResponse, responses=_ACTION_RESPONSES
)
def restart_service(project_id: str, service_name: str, _: dict = Depends(get_current_user)) -> ActionResponse:
    return _perform_action(project_id, service_name, "restart")


@router.post("/{project_id}/services/{service_name}/pause", response_model=ActionResponse, responses=_ACTION_RESPONSES)
def pause_service(project_id: str, service_name: str, _: dict = Depends(get_current_user)) -> ActionResponse:
    return _perform_action(project_id, service_name, "pause")


@router.post(
    "/{project_id}/services/{service_name}/unpause", response_model=ActionResponse, responses=_ACTION_RESPONSES
)
def unpause_service(project_id: str, service_name: str, _: dict = Depends(get_current_user)) -> ActionResponse:
    return _perform_action(project_id, service_name, "unpause")
