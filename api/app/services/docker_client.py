import docker

from app.constants import COMPOSE_LABEL_PROJECT, COMPOSE_LABEL_SERVICE, CONTAINER_UNKNOWN


class DockerClientService:
    """Thin wrapper around the Docker SDK client."""

    def client(self) -> docker.DockerClient:
        return docker.from_env()

    def get_container_for_service(self, project_id: str, service_name: str):
        """Return the Docker container for a given compose service, or None."""
        for container in self.client().containers.list(all=True):
            labels = container.labels
            if (
                labels.get(COMPOSE_LABEL_PROJECT) == project_id
                and labels.get(COMPOSE_LABEL_SERVICE) == service_name
            ):
                return container
        return None

    def get_all_containers_for_project(self, project_id: str) -> list:
        """Return all containers belonging to a compose project."""
        return [
            c
            for c in self.client().containers.list(all=True)
            if c.labels.get(COMPOSE_LABEL_PROJECT) == project_id
        ]

    def get_container_status(self, project_id: str, service_name: str) -> str:
        """Return the status string for a service container, or CONTAINER_UNKNOWN."""
        container = self.get_container_for_service(project_id, service_name)
        return container.status if container is not None else CONTAINER_UNKNOWN


docker_client = DockerClientService()
