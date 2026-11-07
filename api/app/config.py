from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings


INSECURE_SECRET_KEY = "change-me-in-production"  # noqa: S105 — sentinel default, guarded in production


# Environments in which the sentinel SECRET_KEY is tolerated. Any other value
# (production, staging, a typo...) must provide a real secret.
_SENTINEL_SECRET_ALLOWED_ENVIRONMENTS: frozenset[str] = frozenset({"development", "test"})


class InsecureConfigurationError(RuntimeError):
    """Raised when a production deployment is started with insecure defaults."""


class Settings(BaseSettings):
    """Application configuration loaded from environment variables or .env file."""

    # Deployment environment: "development" (default), "test" or "production".
    environment: str = "development"

    secret_key: str = INSECURE_SECRET_KEY
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # LDAP (optional — leave empty to disable)
    ldap_server: str = ""
    ldap_base_dn: str = ""
    ldap_bind_dn: str = ""
    ldap_bind_password: str = ""

    # Local admin fallback (used when LDAP is not configured).
    # Prefer admin_password_hash (a bcrypt hash); admin_password is a
    # plaintext fallback for local development only.
    admin_username: str = "admin"
    admin_password: str = ""
    admin_password_hash: str = ""

    # Path where docker-compose project directories are stored
    projects_path: str = "/projects"

    # Allowed CORS origins
    cors_origins: list[str] = [
        "http://localhost:3000",  # no-hardcoded-localhost: disable -- dev default, override via CORS_ORIGINS
        "http://localhost:5173",  # no-hardcoded-localhost: disable -- dev default, override via CORS_ORIGINS
    ]

    model_config = {"env_file": ".env"}

    @model_validator(mode="after")
    def _guard_production(self) -> "Settings":
        """Reject insecure defaults outside explicit development/test environments."""
        environment = self.environment.strip().lower()
        problems: list[str] = []
        if (
            self.secret_key == INSECURE_SECRET_KEY or not self.secret_key
        ) and environment not in _SENTINEL_SECRET_ALLOWED_ENVIRONMENTS:
            problems.append("secret_key must be set to a strong, non-default value")
        if environment == "production" and not self.ldap_server and not self.admin_password_hash:
            problems.append(
                "a local admin requires admin_password_hash (bcrypt); "
                "plaintext admin_password is not allowed in production"
            )
        if problems:
            raise InsecureConfigurationError("; ".join(problems))
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
