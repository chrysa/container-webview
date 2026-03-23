from __future__ import annotations

import typing
from enum import StrEnum

if typing.TYPE_CHECKING:
    from typing import Final


class DockerComposeLabel(StrEnum):
    """Docker Compose metadata labels attached to every container."""

    PROJECT = "com.docker.compose.project"
    SERVICE = "com.docker.compose.service"


class ContainerState(StrEnum):
    """Container lifecycle states as returned by the Docker SDK."""

    EXITED = "exited"
    RESTARTING = "restarting"
    RUNNING = "running"
    UNKNOWN = "unknown"


class HealthState(StrEnum):
    """Docker healthcheck states."""

    UNHEALTHY = "unhealthy"
    STARTING = "starting"


class AlertLevel(StrEnum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class TokenType(StrEnum):
    """OAuth2 token types."""

    BEARER = "bearer"


# ── Error message templates ────────────────────────────────────────────────
# Use str.format() for interpolation where a {} placeholder is present.
ERR_PROJECT_NOT_FOUND: Final[str] = "Project not found"
ERR_SERVICE_NOT_FOUND: Final[str] = "Service '{}' not found"
ERR_CONTAINER_NOT_FOUND: Final[str] = "No running container for '{}' (start via compose first)"
ERR_UNKNOWN_ACTION: Final[str] = "Unknown action: {}"
ERR_INVALID_TOKEN: Final[str] = "Invalid or expired token"
ERR_INVALID_CREDENTIALS: Final[str] = "Invalid credentials"

# ── JWT / OAuth2 ───────────────────────────────────────────────────────────
JWT_CLAIM_SUB: Final[str] = "sub"

# ── API versioning ────────────────────────────────────────────────────────
API_V1_PREFIX: Final[str] = "/api/v1"
OAUTH2_TOKEN_URL: Final[str] = "/api/v1/auth/login"
