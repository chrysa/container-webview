from __future__ import annotations

import typing

import docker

from app.constants import ContainerState, DockerComposeLabel

if typing.TYPE_CHECKING:
    from docker.models.containers import Container


class DockerClientService:
    """Thin wrapper around the Docker SDK client."""

    def client(self) -> docker.DockerClient:
        """Return a Docker SDK client connected to the local daemon."""
        return docker.from_env()

    def get_container_for_service(self, project_id: str, service_name: str) -> Container | None:
        """Return the Docker container matching a Compose service, or None."""
        for container in self.client().containers.list(all=True):
            labels = container.labels
            if (
                labels.get(DockerComposeLabel.PROJECT) == project_id
                and labels.get(DockerComposeLabel.SERVICE) == service_name
            ):
                return container
        return None

    def get_all_containers_for_project(self, project_id: str) -> list[Container]:
        """Return all containers belonging to a Compose project."""
        return [
            container
            for container in self.client().containers.list(all=True)
            if container.labels.get(DockerComposeLabel.PROJECT) == project_id
        ]

    def get_container_status(self, project_id: str, service_name: str) -> str:
        """Return the status of a service container, or ContainerState.UNKNOWN."""
        container = self.get_container_for_service(project_id, service_name)
        return container.status if container is not None else ContainerState.UNKNOWN


docker_client = DockerClientService()
