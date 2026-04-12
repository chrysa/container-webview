import contextlib
from datetime import UTC
from datetime import datetime

from fastapi import APIRouter
from fastapi import Depends
from pydantic import BaseModel

from app.security import get_current_user
from app.services.docker_client import get_docker_client
from docker.errors import DockerException


router = APIRouter()


class Alert(BaseModel):
    id: str
    level: str  # "info" | "warning" | "critical"
    project: str
    service: str
    message: str
    timestamp: str


def _container_alerts() -> list[Alert]:
    alerts = []
    with contextlib.suppress(DockerException):
        client = get_docker_client()
        for container in client.containers.list(all=True):
            project = container.labels.get("com.docker.compose.project", "")
            service = container.labels.get("com.docker.compose.service", container.name)
            if not project:
                continue

            now = datetime.now(UTC).isoformat()

            if container.status == "exited":
                exit_code = container.attrs.get("State", {}).get("ExitCode", 0)
                level = "critical" if exit_code != 0 else "info"
                alerts.append(
                    Alert(
                        id=f"{container.short_id}-exited",
                        level=level,
                        project=project,
                        service=service,
                        message=f"Container arrêté (code {exit_code})",
                        timestamp=now,
                    )
                )

            elif container.status == "restarting":
                alerts.append(
                    Alert(
                        id=f"{container.short_id}-restart",
                        level="warning",
                        project=project,
                        service=service,
                        message="Container en cours de redémarrage",
                        timestamp=now,
                    )
                )

            health = container.attrs.get("State", {}).get("Health", {})
            if health.get("Status") == "unhealthy":
                alerts.append(
                    Alert(
                        id=f"{container.short_id}-health",
                        level="critical",
                        project=project,
                        service=service,
                        message="Healthcheck échoué",
                        timestamp=now,
                    )
                )
            elif health.get("Status") == "starting":
                alerts.append(
                    Alert(
                        id=f"{container.short_id}-starting",
                        level="info",
                        project=project,
                        service=service,
                        message="Healthcheck en attente (starting)",
                        timestamp=now,
                    )
                )

    return alerts


@router.get("", response_model=list[Alert])
def get_alerts(_: dict = Depends(get_current_user)) -> list[Alert]:
    return _container_alerts()
