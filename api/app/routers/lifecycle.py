from typing import Annotated
from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from pydantic import BaseModel

from app.constants import ERR_CONTAINER_NOT_FOUND
from app.constants import ERR_PROJECT_NOT_FOUND
from app.constants import ERR_SERVICE_NOT_FOUND
from app.security import security
from app.services.lifecycle_service import lifecycle_service


router = APIRouter()

_CurrentUser = Annotated[dict, Depends(security.get_current_user)]
_NOT_FOUND: dict[int | str, dict[str, Any]] = {
    400: {"description": "Unknown action"},
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
        container_status = lifecycle_service.perform(project_id, service_name, action)
    except ValueError as exc:
        detail = str(exc)
        status_code = (
            404
            if detail
            in (
                ERR_PROJECT_NOT_FOUND,
                ERR_SERVICE_NOT_FOUND.format(service_name),
                ERR_CONTAINER_NOT_FOUND.format(service_name),
            )
            else 400
        )
        raise HTTPException(status_code=status_code, detail=detail) from exc
    return ActionResponse(service=service_name, action=action, status=container_status)


@router.post(  # fastapi-missing-links: disable -- action payloads are not HATEOAS resources
    "/{project_id}/services/{service_name}/start",
    response_model=ActionResponse,
    responses=_NOT_FOUND,
)
def start_service(project_id: str, service_name: str, _: _CurrentUser) -> ActionResponse:
    """Start a stopped service container."""
    return _run(project_id, service_name, "start")


@router.post(  # fastapi-missing-links: disable -- action payloads are not HATEOAS resources
    "/{project_id}/services/{service_name}/stop",
    response_model=ActionResponse,
    responses=_NOT_FOUND,
)
def stop_service(project_id: str, service_name: str, _: _CurrentUser) -> ActionResponse:
    """Stop a running service container."""
    return _run(project_id, service_name, "stop")


@router.post(  # fastapi-missing-links: disable -- action payloads are not HATEOAS resources
    "/{project_id}/services/{service_name}/restart",
    response_model=ActionResponse,
    responses=_NOT_FOUND,
)
def restart_service(project_id: str, service_name: str, _: _CurrentUser) -> ActionResponse:
    """Restart a service container."""
    return _run(project_id, service_name, "restart")


@router.post(  # fastapi-missing-links: disable -- action payloads are not HATEOAS resources
    "/{project_id}/services/{service_name}/pause",
    response_model=ActionResponse,
    responses=_NOT_FOUND,
)
def pause_service(project_id: str, service_name: str, _: _CurrentUser) -> ActionResponse:
    """Pause a running service container."""
    return _run(project_id, service_name, "pause")


@router.post(  # fastapi-missing-links: disable -- action payloads are not HATEOAS resources
    "/{project_id}/services/{service_name}/unpause",
    response_model=ActionResponse,
    responses=_NOT_FOUND,
)
def unpause_service(project_id: str, service_name: str, _: _CurrentUser) -> ActionResponse:
    """Resume a paused service container."""
    return _run(project_id, service_name, "unpause")
