from app.constants import (
    ERR_CONTAINER_NOT_FOUND,
    ERR_PROJECT_NOT_FOUND,
    ERR_SERVICE_NOT_FOUND,
    ERR_UNKNOWN_ACTION,
)
from app.services.docker_client import docker_client
from app.services.project_manager import project_manager


class LifecycleService:
    """Executes start/stop/restart/pause/unpause/kill on Compose service containers."""

    _VALID_ACTIONS: frozenset[str] = frozenset({
        "kill", "pause", "restart", "start", "stop", "unpause",
    })

    def perform(self, project_id: str, service_name: str, action: str) -> str:
        """Execute a lifecycle action and return the resulting container status.

        Raises:
            ValueError: if action, project, service, or container is not found.
            docker.errors.APIError: propagated if the Docker operation fails.
        """
        if action not in self._VALID_ACTIONS:
            raise ValueError(ERR_UNKNOWN_ACTION.format(action))

        project = project_manager.load(project_id)
        if project is None:
            raise ValueError(ERR_PROJECT_NOT_FOUND)

        if service_name not in {svc.name for svc in project.services}:
            raise ValueError(ERR_SERVICE_NOT_FOUND.format(service_name))

        container = docker_client.get_container_for_service(project_id, service_name)
        if container is None:
            raise ValueError(ERR_CONTAINER_NOT_FOUND.format(service_name))

        getattr(container, action)()
        container.reload()
        return container.status


lifecycle_service = LifecycleService()
