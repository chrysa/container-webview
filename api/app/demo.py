"""Demo-mode fixtures.

When ``settings.demo_mode`` is enabled, every read path that would otherwise
talk to the Docker socket or the projects directory serves the realistic inline
fixtures defined here instead. This lets the whole app be explored without any
real credentials or a running Docker daemon. The fixtures deliberately match the
Pydantic schemas returned by the routers so the frontend behaves identically.

Built as plain dicts (not the router models) to avoid import cycles; each router
adapts them into its own response model.
"""

from __future__ import annotations

from datetime import UTC
from datetime import datetime
from typing import Any


DEMO_USERNAME = "demo"
DEMO_PASSWORD = "demo"  # noqa: S105  # nosec B105 — public demo credentials, not a secret

_DEMO_PROJECT_ID = "demo-shop"
_DEMO_PROJECT_ID_2 = "demo-blog"


def _now() -> str:
    return datetime.now(UTC).isoformat()


# ── Projects ─────────────────────────────────────────────────────────────────
# Shape mirrors app.services.project_manager.ProjectModel / ServiceModel.
_DEMO_PROJECTS: list[dict[str, Any]] = [
    {
        "id": _DEMO_PROJECT_ID,
        "name": "Demo Shop",
        "path": f"/projects/{_DEMO_PROJECT_ID}",
        "compose_file": "docker-compose.yml",
        "networks": ["frontend", "backend"],
        "services": [
            {
                "name": "web",
                "image": "nginx:1.27-alpine",
                "ports": ["80", "443"],
                "depends_on": ["api"],
                "networks": ["frontend"],
                "volumes": ["web-static"],
                "environment": {"TZ": "UTC"},
                "healthcheck": {"test": ["CMD", "curl", "-f", "http://localhost"]},
            },
            {
                "name": "api",
                "image": "demo/shop-api:2.3.1",
                "ports": ["8000"],
                "depends_on": ["db", "cache"],
                "networks": ["frontend", "backend"],
                "volumes": [],
                "environment": {"DATABASE_URL": "postgres://db:5432/shop", "LOG_LEVEL": "info"},
                "healthcheck": None,
            },
            {
                "name": "db",
                "image": "postgres:16-alpine",
                "ports": ["5432"],
                "depends_on": [],
                "networks": ["backend"],
                "volumes": ["db-data"],
                "environment": {"POSTGRES_DB": "shop"},
                "healthcheck": {"test": ["CMD-SHELL", "pg_isready"]},
            },
            {
                "name": "cache",
                "image": "redis:7-alpine",
                "ports": ["6379"],
                "depends_on": [],
                "networks": ["backend"],
                "volumes": [],
                "environment": {},
                "healthcheck": None,
            },
        ],
    },
    {
        "id": _DEMO_PROJECT_ID_2,
        "name": "Demo Blog",
        "path": f"/projects/{_DEMO_PROJECT_ID_2}",
        "compose_file": "docker-compose.yml",
        "networks": ["default"],
        "services": [
            {
                "name": "ghost",
                "image": "ghost:5-alpine",
                "ports": ["2368"],
                "depends_on": ["mysql"],
                "networks": ["default"],
                "volumes": ["ghost-content"],
                "environment": {"NODE_ENV": "production"},
                "healthcheck": None,
            },
            {
                "name": "mysql",
                "image": "mysql:8",
                "ports": ["3306"],
                "depends_on": [],
                "networks": ["default"],
                "volumes": ["mysql-data"],
                "environment": {"MYSQL_DATABASE": "ghost"},
                "healthcheck": {"test": ["CMD", "mysqladmin", "ping"]},
            },
        ],
    },
]

# Per-service runtime status used by topology / metrics fixtures.
_DEMO_STATUS: dict[str, dict[str, str]] = {
    _DEMO_PROJECT_ID: {
        "web": "running",
        "api": "running",
        "db": "running",
        "cache": "exited",
    },
    _DEMO_PROJECT_ID_2: {
        "ghost": "running",
        "mysql": "restarting",
    },
}


def list_projects() -> list[dict[str, Any]]:
    """Return all demo projects (full copies, callers may mutate freely)."""
    return [dict(project) for project in _DEMO_PROJECTS]


def load_project(project_id: str) -> dict[str, Any] | None:
    """Return a single demo project by id, or None if unknown."""
    for project in _DEMO_PROJECTS:
        if project["id"] == project_id:
            return dict(project)
    return None


def service_status(project_id: str, service_name: str) -> str:
    """Return the fixture runtime status for a service, or 'unknown'."""
    return _DEMO_STATUS.get(project_id, {}).get(service_name, "unknown")


# ── Metrics ──────────────────────────────────────────────────────────────────
# Shape mirrors app.routers.metrics.ServiceMetrics.
def project_metrics(project_id: str) -> list[dict[str, Any]]:
    """Return realistic per-service resource metrics for a demo project."""
    project = load_project(project_id)
    if not project:
        return []
    samples = [
        (12.4, 128.0, 512.0, 3.2, 1.1, 5.0, 2.0),
        (37.8, 256.0, 1024.0, 18.7, 9.4, 41.0, 12.0),
        (4.1, 96.0, 512.0, 1.0, 0.5, 80.0, 30.0),
        (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
    ]
    result: list[dict[str, Any]] = []
    for index, service in enumerate(project["services"]):
        status = service_status(project_id, service["name"])
        cpu, mem_use, mem_lim, rx, tx, br, bw = samples[index % len(samples)]
        if status != "running":
            cpu = mem_use = rx = tx = 0.0
        result.append(
            {
                "service": service["name"],
                "container_id": f"demo{index:02d}{project_id[:4]}",
                "status": status,
                "cpu_percent": cpu,
                "mem_usage_mb": mem_use,
                "mem_limit_mb": mem_lim,
                "mem_percent": round((mem_use / mem_lim) * 100, 2) if mem_lim else 0.0,
                "net_rx_mb": rx,
                "net_tx_mb": tx,
                "block_read_mb": br,
                "block_write_mb": bw,
            }
        )
    return result


# ── Alerts ───────────────────────────────────────────────────────────────────
# Shape mirrors app.routers.alerts.Alert.
def alerts() -> list[dict[str, Any]]:
    """Return active demo alerts derived from the fixture service statuses."""
    now = _now()
    return [
        {
            "id": "demo-cache-exited",
            "level": "critical",
            "project": _DEMO_PROJECT_ID,
            "service": "cache",
            "message": "Container stopped (exit code 137)",
            "timestamp": now,
        },
        {
            "id": "demo-mysql-restart",
            "level": "warning",
            "project": _DEMO_PROJECT_ID_2,
            "service": "mysql",
            "message": "Container is restarting",
            "timestamp": now,
        },
    ]
