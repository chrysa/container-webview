from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

from app.config import get_settings
from app.models.hateoas import ProjectLinks



class ServiceModel(BaseModel):
    """Schema for a single service entry in a Compose file."""
    name: str
    image: str | None = None
    ports: list[str] = []
    depends_on: list[str] = []
    networks: list[str] = []
    volumes: list[str] = []
    environment: dict = {}
    healthcheck: dict | None = None


class ProjectModel(BaseModel):
    """High-level representation of a detected Compose project."""
    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    path: str
    compose_file: str
    services: list[ServiceModel] = []
    networks: list[str] = []
    links: ProjectLinks | None = Field(None, alias="_links")


class ProjectManager:
    """Discovers and parses Docker Compose projects from the configured projects directory."""
    _COMPOSE_CANDIDATES: tuple[str, ...] = (
        "docker-compose.yml",
        "docker-compose.yaml",
        "compose.yml",
        "compose.yaml",
    )
    _YAML_KEY_SERVICES: str = "services"
    _YAML_KEY_NETWORKS: str = "networks"
    _ERR_INVALID_PATH: str = "Invalid project path: {}"

    # ── Path helpers ────────────────────────────────────────────────────────

    def _safe_project_path(self, project_id: str) -> Path:
        """Resolve and validate path stays within projects_path (path-traversal guard)."""
        base = Path(get_settings().projects_path).resolve()
        target = (base / project_id).resolve()
        if not str(target).startswith(str(base)):
            raise ValueError(self._ERR_INVALID_PATH.format(project_id))
        return target

    # ── Compose parsing helpers ─────────────────────────────────────────────

    @staticmethod
    def _parse_compose(compose_path: Path) -> dict[str, object]:
        """Read and parse a Compose YAML file."""
        with open(compose_path) as fh:
            return yaml.safe_load(fh) or {}

    @staticmethod
    def _normalize_ports(raw: list | None) -> list[str]:
        if not raw:
            return []
        result = []
        for p in raw:
            result.append(str(p.get("target", "")) if isinstance(p, dict) else str(p))
        return result

    @staticmethod
    def _normalize_list_or_dict_keys(raw: list | dict | None) -> list[str]:
        """Work for both depends_on and networks which can be list or dict."""
        if not raw:
            return []
        if isinstance(raw, list):
            return raw
        if isinstance(raw, dict):
            return list(raw.keys())
        return []

    @staticmethod
    def _normalize_volumes(raw: list | None) -> list[str]:
        """Extract host-side paths from all volume spec formats."""
        if not raw:
            return []
        result = []
        for v in raw:
            if isinstance(v, dict):
                result.append(v.get("source", ""))
            else:
                result.append(str(v).split(":")[0])
        return [v for v in result if v]

    @staticmethod
    def _normalize_environment(raw: dict | list | None) -> dict[str, str]:
        """Normalise both dict and KEY=VALUE list environment specs."""
        if not raw:
            return {}
        if isinstance(raw, dict):
            return {k: str(v) for k, v in raw.items() if v is not None}
        if isinstance(raw, list):
            result: dict[str, str] = {}
            for item in raw:
                if "=" in item:
                    k, v = item.split("=", 1)
                    result[k] = v
            return result
        return {}

    def _build_service(self, name: str, conf: dict[str, object]) -> ServiceModel:
        return ServiceModel(
            name=name,
            image=conf.get("image"),
            ports=self._normalize_ports(conf.get("ports")),
            depends_on=self._normalize_list_or_dict_keys(conf.get("depends_on")),
            networks=self._normalize_list_or_dict_keys(conf.get("networks")),
            volumes=self._normalize_volumes(conf.get("volumes")),
            environment=self._normalize_environment(conf.get("environment")),
            healthcheck=conf.get("healthcheck"),
        )

    # ── Public API ──────────────────────────────────────────────────────────

    def load(self, project_id: str) -> ProjectModel | None:
        """Return the parsed *ProjectModel* for *project_id*, or ``None`` if not found."""
        project_model: ProjectModel | None = None
        try:
            project_dir = self._safe_project_path(project_id)
        except ValueError:
            project_dir = None

        if project_dir is not None and project_dir.is_dir():
            compose_file = next(
                (c for c in self._COMPOSE_CANDIDATES if (project_dir / c).exists()),
                None,
            )
            if compose_file:
                data = self._parse_compose(project_dir / compose_file)
                services = [
                    self._build_service(name, conf if isinstance(conf, dict) else {})
                    for name, conf in (data.get(self._YAML_KEY_SERVICES) or {}).items()
                ]
                project_model = ProjectModel(
                    id=project_id,
                    name=project_id.replace("-", " ").replace("_", " ").title(),
                    path=str(project_dir),
                    compose_file=compose_file,
                    services=services,
                    networks=list((data.get(self._YAML_KEY_NETWORKS) or {}).keys()),
                )
        return project_model

    def list_all(self) -> list[ProjectModel]:
        """Return all valid projects found under *projects_path*."""
        base = Path(get_settings().projects_path)
        projects: list[ProjectModel] = []
        if base.exists():
            for entry in sorted(base.iterdir()):
                if entry.is_dir():
                    project = self.load(entry.name)
                    if project:
                        projects.append(project)
        return projects


project_manager = ProjectManager()
