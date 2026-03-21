from fastapi import APIRouter, Depends
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.security import get_current_user
from app.services.docker_client import get_docker_client

router = APIRouter()


class Alert(BaseModel):
    id: str
    level: str          # "info" | "warning" | "critical"
    project: str
    service: str
    message: str
    timestamp: str


def _container_alerts() -> List[Alert]:
    alerts = []
    try:
        client = get_docker_client()
        for container in client.containers.list(all=True):
            project = container.labels.get("com.docker.compose.project", "")
            service = container.labels.get("com.docker.compose.service", container.name)
            if not project:
                continue

            now = datetime.utcnow().isoformat()

            if container.status == "exited":
                exit_code = container.attrs.get("State", {}).get("ExitCode", 0)
                level = "critical" if exit_code != 0 else "info"
                alerts.append(Alert(
                    id=f"{container.short_id}-exited",
                    level=level,
                    project=project,
                    service=service,
                    message=f"Container arrêté (code {exit_code})",
                    timestamp=now,
                ))

            elif container.status == "restarting":
                alerts.append(Alert(
                    id=f"{container.short_id}-restart",
                    level="warning",
                    project=project,
                    service=service,
                    message="Container en cours de redémarrage",
                    timestamp=now,
                ))

            # Santé
            health = container.attrs.get("State", {}).get("Health", {})
            if health.get("Status") == "unhealthy":
                alerts.append(Alert(
                    id=f"{container.short_id}-health",
                    level="critical",
                    project=project,
                    service=service,
                    message="Healthcheck échoué",
                    timestamp=now,
                ))
            elif health.get("Status") == "starting":
                alerts.append(Alert(
                    id=f"{container.short_id}-starting",
                    level="info",
                    project=project,
                    service=service,
                    message="Healthcheck en attente (starting)",
                    timestamp=now,
                ))

    except Exception:
        pass
    return alerts


@router.get("", response_model=List[Alert])
def get_alerts(_: dict = Depends(get_current_user)):
    return _container_alerts()
