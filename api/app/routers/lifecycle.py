from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.constants import (
    ERR_CONTAINER_NOT_FOUND,
    ERR_PROJECT_NOT_FOUND,
    ERR_SERVICE_NOT_FOUND,
)
from app.security import security
from app.services.lifecycle_service import lifecycle_service

router = APIRouter()

_CurrentUser = Annotated[dict, Depends(security.get_current_user)]
_NOT_FOUND = {
    400: {"description": "Unknown action"},
    404: {"description": "Project, service or container not found"},
}


class ActionResponse(BaseModel):
    """Result of a lifecycle action on a service container."""

    service: str
    action: str
    status: str
    message: str = ""


def _run(project_id: str, service_name: str, action: str) -> ActionResponse:
    """Delegate a lifecycle action to the service, translating ValueError to HTTPException."""
    try:
        container_status = lifecycle_service.perform(project_id, service_name, action)
    except ValueError as exc:
        detail = str(exc)
        status_code = 404 if detail in (
            ERR_PROJECT_NOT_FOUND,
            ERR_SERVICE_NOT_FOUND.format(service_name),
            ERR_CONTAINER_NOT_FOUND.format(service_name),
        ) else 400
        raise HTTPException(status_code=status_code, detail=detail) from exc
    return ActionResponse(service=service_name, action=action, status=container_status)


@router.post("/{project_id}/services/{service_name}/start", responses=_NOT_FOUND)
def start_service(project_id: str, service_name: str, _: _CurrentUser) -> ActionResponse:
    """Start a stopped service container."""
    return _run(project_id, service_name, "start")


@router.post("/{project_id}/services/{service_name}/stop", responses=_NOT_FOUND)
def stop_service(project_id: str, service_name: str, _: _CurrentUser) -> ActionResponse:
    """Stop a running service container."""
    return _run(project_id, service_name, "stop")


@router.post("/{project_id}/services/{service_name}/restart", responses=_NOT_FOUND)
def restart_service(project_id: str, service_name: str, _: _CurrentUser) -> ActionResponse:
    """Restart a service container."""
    return _run(project_id, service_name, "restart")


@router.post("/{project_id}/services/{service_name}/pause", responses=_NOT_FOUND)
def pause_service(project_id: str, service_name: str, _: _CurrentUser) -> ActionResponse:
    """Pause a running service container."""
    return _run(project_id, service_name, "pause")


@router.post("/{project_id}/services/{service_name}/unpause", responses=_NOT_FOUND)
def unpause_service(project_id: str, service_name: str, _: _CurrentUser) -> ActionResponse:
    """Resume a paused service container."""
    return _run(project_id, service_name, "unpause")
