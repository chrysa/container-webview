import docker.models.containers

import docker


_client: docker.DockerClient | None = None


def get_docker_client() -> docker.DockerClient:
    global _client
    if _client is None:
        _client = docker.from_env()
    return _client


def get_container_for_service(
    project_id: str,
    service_name: str,
) -> docker.models.containers.Container | None:
    """Return the Docker container for a Compose service, or None."""
    client = get_docker_client()
    for container in client.containers.list(all=True):
        labels = container.labels
        if (
            labels.get("com.docker.compose.project") == project_id
            and labels.get("com.docker.compose.service") == service_name
        ):
            return container
    return None


def get_all_containers_for_project(project_id: str) -> list[docker.models.containers.Container]:
    """Return all containers belonging to a Compose project."""
    client = get_docker_client()
    return [
        container
        for container in client.containers.list(all=True)
        if container.labels.get("com.docker.compose.project", "") == project_id
    ]
