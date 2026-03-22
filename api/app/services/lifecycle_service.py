from fastapi import HTTPException
from pydantic import BaseModel

from app.constants import (
    ERR_CONTAINER_NOT_FOUND,
    ERR_PROJECT_NOT_FOUND,
    ERR_SERVICE_NOT_FOUND,
    ERR_UNKNOWN_ACTION,
)
from app.services.docker_client import docker_client
from app.services.project_manager import project_manager


class ActionResponse(BaseModel):
    service: str
    action: str
    status: str
    message: str = ""


class LifecycleService:
    _VALID_ACTIONS: frozenset[str] = frozenset({"start", "stop", "restart", "pause", "unpause", "kill"})

    def perform(self, project_id: str, service_name: str, action: str) -> ActionResponse:
        if action not in self._VALID_ACTIONS:
            raise HTTPException(status_code=400, detail=ERR_UNKNOWN_ACTION.format(action))

        project = project_manager.load(project_id)
        if not project:
            raise HTTPException(status_code=404, detail=ERR_PROJECT_NOT_FOUND)

        if service_name not in {s.name for s in project.services}:
            raise HTTPException(status_code=404, detail=ERR_SERVICE_NOT_FOUND.format(service_name))

        container = docker_client.get_container_for_service(project_id, service_name)
        if container is None:
            raise HTTPException(
                status_code=404,
                detail=ERR_CONTAINER_NOT_FOUND.format(service_name),
            )

        try:
            getattr(container, action)()
            container.reload()
            return ActionResponse(service=service_name, action=action, status=container.status)
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc


lifecycle_service = LifecycleService()
