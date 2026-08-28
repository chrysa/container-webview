from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings


INSECURE_SECRET_KEY = "change-me-in-production"  # noqa: S105 — sentinel default, guarded in production


class InsecureConfigurationError(RuntimeError):
    """Raised when a production deployment is started with insecure defaults."""


class Settings(BaseSettings):
    """Application configuration loaded from environment variables or .env file."""

    # Deployment environment: "development" (default) or "production".
    environment: str = "development"

    secret_key: str = INSECURE_SECRET_KEY
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # LDAP (optionnel — laisser vide pour désactiver)
    ldap_server: str = ""
    ldap_base_dn: str = ""
    ldap_bind_dn: str = ""
    ldap_bind_password: str = ""  # nosec B105 — set via LDAP_BIND_PASSWORD env var

    # Local admin fallback (used when LDAP is not configured).
    # Prefer admin_password_hash (a bcrypt hash); admin_password is a
    # plaintext fallback for local development only.
    admin_username: str = "admin"
    admin_password: str = ""
    admin_password_hash: str = ""

    # CORS — allowed origins (comma-separated via env var CORS_ORIGINS)
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]  # no-hardcoded-localhost: disable

    # Chemin monté où sont stockés les docker-compose des projets
    projects_path: str = "/projects"

    # Allowed CORS origins
    cors_origins: list[str] = [
        "http://localhost:3000",  # no-hardcoded-localhost: disable -- dev default, override via CORS_ORIGINS
        "http://localhost:5173",  # no-hardcoded-localhost: disable -- dev default, override via CORS_ORIGINS
    ]

    class Config:
        env_file = ".env"


settings = Settings()

    @model_validator(mode="after")
    def _guard_production(self) -> "Settings":
        """Reject insecure defaults when running in production."""
        if self.environment.lower() != "production":
            return self
        problems: list[str] = []
        if self.secret_key == INSECURE_SECRET_KEY or not self.secret_key:
            problems.append("secret_key must be set to a strong, non-default value")
        if not self.ldap_server and not self.admin_password_hash:
            problems.append(
                "a local admin requires admin_password_hash (bcrypt); "
                "plaintext admin_password is not allowed in production"
            )
        if problems:
            raise InsecureConfigurationError("; ".join(problems))
        return self


def get_settings() -> Settings:
    """Dependency-injectable settings accessor."""
    return settings
