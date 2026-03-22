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
    service: str
    action: str
    status: str
    message: str = ""


def _run(project_id: str, service_name: str, action: str) -> ActionResponse:
    try:
        result = lifecycle_service.perform(project_id, service_name, action)
        return ActionResponse(
            service=service_name, action=action, status=result["status"]
        )
    except ValueError as exc:
        msg = str(exc)
        if ERR_PROJECT_NOT_FOUND in msg:
            raise HTTPException(status_code=404, detail=ERR_PROJECT_NOT_FOUND)
        if "Service" in msg:
            raise HTTPException(status_code=404, detail=ERR_SERVICE_NOT_FOUND.format(service_name))
        if "container" in msg.lower():
            raise HTTPException(status_code=404, detail=ERR_CONTAINER_NOT_FOUND.format(service_name))
        raise HTTPException(status_code=400, detail=msg)


@router.post("/{project_id}/services/{service_name}/start", responses=_NOT_FOUND)
def start_service(project_id: str, service_name: str, _: _CurrentUser) -> ActionResponse:
    return _run(project_id, service_name, "start")


@router.post("/{project_id}/services/{service_name}/stop", responses=_NOT_FOUND)
def stop_service(project_id: str, service_name: str, _: _CurrentUser) -> ActionResponse:
    return _run(project_id, service_name, "stop")


@router.post("/{project_id}/services/{service_name}/restart", responses=_NOT_FOUND)
def restart_service(project_id: str, service_name: str, _: _CurrentUser) -> ActionResponse:
    return _run(project_id, service_name, "restart")


@router.post("/{project_id}/services/{service_name}/pause", responses=_NOT_FOUND)
def pause_service(project_id: str, service_name: str, _: _CurrentUser) -> ActionResponse:
    return _run(project_id, service_name, "pause")


@router.post("/{project_id}/services/{service_name}/unpause", responses=_NOT_FOUND)
def unpause_service(project_id: str, service_name: str, _: _CurrentUser) -> ActionResponse:
    return _run(project_id, service_name, "unpause")
