# Docker Compose label keys (attached to every container by the Compose engine)
COMPOSE_LABEL_PROJECT: str = "com.docker.compose.project"
COMPOSE_LABEL_SERVICE: str = "com.docker.compose.service"

# Container lifecycle states (as returned by the Docker SDK)
CONTAINER_EXITED: str = "exited"
CONTAINER_RESTARTING: str = "restarting"
CONTAINER_RUNNING: str = "running"
CONTAINER_UNKNOWN: str = "unknown"

# Docker health-check states
HEALTH_UNHEALTHY: str = "unhealthy"
HEALTH_STARTING: str = "starting"

# Alert severity levels
ALERT_INFO: str = "info"
ALERT_WARNING: str = "warning"
ALERT_CRITICAL: str = "critical"

# HTTP error detail strings (user-facing)
ERR_PROJECT_NOT_FOUND: str = "Project not found"
ERR_SERVICE_NOT_FOUND: str = "Service '{}' not found"
ERR_CONTAINER_NOT_FOUND: str = "No running container for '{}' (start via compose first)"
ERR_UNKNOWN_ACTION: str = "Unknown action: {}"
ERR_INVALID_TOKEN: str = "Invalid or expired token"
ERR_INVALID_CREDENTIALS: str = "Invalid credentials"

# Auth
TOKEN_TYPE_BEARER: str = "bearer"
JWT_CLAIM_SUB: str = "sub"

# OAuth2 token URL
OAUTH2_TOKEN_URL: str = "/api/auth/login"
