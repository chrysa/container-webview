import os
import re
from pathlib import Path
from typing import List, Optional

import yaml
from pydantic import BaseModel

from app.config import settings


class ServiceModel(BaseModel):
    name: str
    image: Optional[str] = None
    ports: List[str] = []
    depends_on: List[str] = []
    networks: List[str] = []
    volumes: List[str] = []
    environment: dict = {}
    healthcheck: Optional[dict] = None


class ProjectModel(BaseModel):
    id: str
    name: str
    path: str
    compose_file: str
    services: List[ServiceModel] = []
    networks: List[str] = []


def _safe_project_path(project_id: str) -> Path:
    """Valide que le chemin résolu reste dans projects_path (sécurité path traversal)."""
    base = Path(settings.projects_path).resolve()
    target = (base / project_id).resolve()
    if not str(target).startswith(str(base)):
        raise ValueError(f"Chemin invalide : {project_id}")
    return target


def _parse_compose(compose_path: Path) -> dict:
    with open(compose_path, "r") as f:
        return yaml.safe_load(f) or {}


def _normalize_ports(ports_raw) -> List[str]:
    if not ports_raw:
        return []
    result = []
    for p in ports_raw:
        if isinstance(p, dict):
            result.append(f"{p.get('target', '')}")
        else:
            result.append(str(p))
    return result


def _normalize_depends(depends_raw) -> List[str]:
    if not depends_raw:
        return []
    if isinstance(depends_raw, list):
        return depends_raw
    if isinstance(depends_raw, dict):
        return list(depends_raw.keys())
    return []


def _normalize_networks(nets_raw) -> List[str]:
    if not nets_raw:
        return []
    if isinstance(nets_raw, list):
        return nets_raw
    if isinstance(nets_raw, dict):
        return list(nets_raw.keys())
    return []


def _normalize_volumes(vols_raw) -> List[str]:
    if not vols_raw:
        return []
    result = []
    for v in vols_raw:
        if isinstance(v, dict):
            result.append(v.get("source", ""))
        else:
            result.append(str(v).split(":")[0])
    return [v for v in result if v]


def _normalize_environment(env_raw) -> dict:
    if not env_raw:
        return {}
    if isinstance(env_raw, dict):
        return {k: str(v) for k, v in env_raw.items() if v is not None}
    if isinstance(env_raw, list):
        result = {}
        for item in env_raw:
            if "=" in item:
                k, v = item.split("=", 1)
                result[k] = v
        return result
    return {}


def load_project(project_id: str) -> Optional[ProjectModel]:
    try:
        project_dir = _safe_project_path(project_id)
    except ValueError:
        return None

    if not project_dir.is_dir():
        return None

    compose_file = None
    for candidate in ["docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"]:
        if (project_dir / candidate).exists():
            compose_file = candidate
            break

    if not compose_file:
        return None

    compose_path = project_dir / compose_file
    data = _parse_compose(compose_path)

    services = []
    for svc_name, svc_conf in (data.get("services") or {}).items():
        if not isinstance(svc_conf, dict):
            svc_conf = {}
        services.append(ServiceModel(
            name=svc_name,
            image=svc_conf.get("image"),
            ports=_normalize_ports(svc_conf.get("ports")),
            depends_on=_normalize_depends(svc_conf.get("depends_on")),
            networks=_normalize_networks(svc_conf.get("networks")),
            volumes=_normalize_volumes(svc_conf.get("volumes")),
            environment=_normalize_environment(svc_conf.get("environment")),
            healthcheck=svc_conf.get("healthcheck"),
        ))

    top_networks = list((data.get("networks") or {}).keys())

    return ProjectModel(
        id=project_id,
        name=project_id.replace("-", " ").replace("_", " ").title(),
        path=str(project_dir),
        compose_file=compose_file,
        services=services,
        networks=top_networks,
    )


def list_projects() -> List[ProjectModel]:
    base = Path(settings.projects_path)
    if not base.exists():
        return []
    projects = []
    for entry in sorted(base.iterdir()):
        if entry.is_dir():
            project = load_project(entry.name)
            if project:
                projects.append(project)
    return projects
