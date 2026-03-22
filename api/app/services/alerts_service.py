from datetime import datetime, timezone

from pydantic import BaseModel

from app.constants import (
    ALERT_CRITICAL,
    ALERT_INFO,
    ALERT_WARNING,
    COMPOSE_LABEL_PROJECT,
    COMPOSE_LABEL_SERVICE,
    CONTAINER_EXITED,
    CONTAINER_RESTARTING,
    HEALTH_STARTING,
    HEALTH_UNHEALTHY,
)
from app.services.docker_client import docker_client


class Alert(BaseModel):
    id: str
    level: str  # ALERT_INFO | ALERT_WARNING | ALERT_CRITICAL
    project: str
    service: str
    message: str
    timestamp: str


class AlertsService:
    def _alerts_for_container(self, container) -> list[Alert]:
        project: str = container.labels.get(COMPOSE_LABEL_PROJECT, "")
        if not project:
            return []

        service: str = container.labels.get(COMPOSE_LABEL_SERVICE, container.name)
        now: str = datetime.now(timezone.utc).isoformat()
        state: dict = container.attrs.get("State", {})
        alerts: list[Alert] = []

        if container.status == CONTAINER_EXITED:
            exit_code: int = state.get("ExitCode", 0)
            alerts.append(Alert(
                id=f"{container.short_id}-exited",
                level=ALERT_CRITICAL if exit_code != 0 else ALERT_INFO,
                project=project,
                service=service,
                message=f"Container stopped (exit code {exit_code})",
                timestamp=now,
            ))
        elif container.status == CONTAINER_RESTARTING:
            alerts.append(Alert(
                id=f"{container.short_id}-restart",
                level=ALERT_WARNING,
                project=project,
                service=service,
                message="Container is restarting",
                timestamp=now,
            ))

        health_status: str = state.get("Health", {}).get("Status", "")
        if health_status == HEALTH_UNHEALTHY:
            alerts.append(Alert(
                id=f"{container.short_id}-health",
                level=ALERT_CRITICAL,
                project=project,
                service=service,
                message="Healthcheck failed",
                timestamp=now,
            ))
        elif health_status == HEALTH_STARTING:
            alerts.append(Alert(
                id=f"{container.short_id}-starting",
                level=ALERT_INFO,
                project=project,
                service=service,
                message="Healthcheck pending (starting)",
                timestamp=now,
            ))

        return alerts

    def get_all_alerts(self) -> list[Alert]:
        result: list[Alert] = []
        try:
            for container in docker_client.client().containers.list(all=True):
                result.extend(self._alerts_for_container(container))
        except Exception:
            pass
        return result


alerts_service = AlertsService()
