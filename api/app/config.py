from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # LDAP (optional — leave empty to disable)
    ldap_server: str = ""
    ldap_base_dn: str = ""
    ldap_bind_dn: str = ""
    ldap_bind_password: str = ""

    # Local admin fallback (used when LDAP is not configured)
    admin_username: str = "admin"
    admin_password: str = "admin"

    # Path where docker-compose project directories are stored
    projects_path: str = "/projects"

    # Allowed CORS origins
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    model_config = {"env_file": ".env"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
