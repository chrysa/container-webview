from __future__ import annotations

import logging
from datetime import datetime, timezone

import docker.errors
from pydantic import BaseModel

from app.constants import AlertLevel, ContainerState, DockerComposeLabel, HealthState
from app.services.docker_client import docker_client

_logger = logging.getLogger(__name__)


class Alert(BaseModel):
    """A single operational alert for a Docker Compose service."""

    id: str
    level: str  # AlertLevel value
    project: str
    service: str
    message: str
    timestamp: str


class AlertsService:
    """Inspects running containers and produces operational alerts."""

    def _alerts_for_container(self, container) -> list[Alert]:
        """Return all alerts generated for a single container."""
        project: str = container.labels.get(DockerComposeLabel.PROJECT, "")
        if not project:
            return []

        service: str = container.labels.get(DockerComposeLabel.SERVICE, container.name)
        now: str = datetime.now(timezone.utc).isoformat()
        state: dict = container.attrs.get("State", {})
        alerts: list[Alert] = []

        if container.status == ContainerState.EXITED:
            exit_code: int = state.get("ExitCode", 0)
            alerts.append(Alert(
                id=f"{container.short_id}-exited",
                level=AlertLevel.CRITICAL if exit_code != 0 else AlertLevel.INFO,
                project=project,
                service=service,
                message=f"Container stopped (exit code {exit_code})",
                timestamp=now,
            ))
        elif container.status == ContainerState.RESTARTING:
            alerts.append(Alert(
                id=f"{container.short_id}-restart",
                level=AlertLevel.WARNING,
                project=project,
                service=service,
                message="Container is restarting",
                timestamp=now,
            ))

        health_status: str = state.get("Health", {}).get("Status", "")
        if health_status == HealthState.UNHEALTHY:
            alerts.append(Alert(
                id=f"{container.short_id}-health",
                level=AlertLevel.CRITICAL,
                project=project,
                service=service,
                message="Healthcheck failed",
                timestamp=now,
            ))
        elif health_status == HealthState.STARTING:
            alerts.append(Alert(
                id=f"{container.short_id}-starting",
                level=AlertLevel.INFO,
                project=project,
                service=service,
                message="Healthcheck pending (starting)",
                timestamp=now,
            ))

        return alerts

    def get_all(self) -> list[Alert]:
        """Return all alerts across every running container."""
        try:
            containers = docker_client.client().containers.list(all=True)
        except docker.errors.DockerException as docker_exc:
            _logger.warning("Docker unavailable — cannot fetch alerts: %s", docker_exc)
            return []
        result: list[Alert] = []
        for container in containers:
            result.extend(self._alerts_for_container(container))
        return result

    def get_for_project(self, project_id: str) -> list[Alert]:
        """Return all alerts for a specific Compose project."""
        return [alert for alert in self.get_all() if alert.project == project_id]


alerts_service = AlertsService()
