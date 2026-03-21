import docker
from typing import Optional

_client: Optional[docker.DockerClient] = None


def get_docker_client() -> docker.DockerClient:
    global _client
    if _client is None:
        _client = docker.from_env()
    return _client


def get_container_for_service(project_id: str, service_name: str):
    """Trouve le container Docker correspondant à un service compose."""
    client = get_docker_client()
    # Docker Compose nomme les containers : <project>-<service>-<n> ou <project>_<service>_<n>
    for container in client.containers.list(all=True):
        labels = container.labels
        compose_project = labels.get("com.docker.compose.project", "")
        compose_service = labels.get("com.docker.compose.service", "")
        if compose_project == project_id and compose_service == service_name:
            return container
    return None


def get_all_containers_for_project(project_id: str):
    client = get_docker_client()
    result = []
    for container in client.containers.list(all=True):
        if container.labels.get("com.docker.compose.project", "") == project_id:
            result.append(container)
    return result
