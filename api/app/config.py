from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    secret_key: str = ""  # nosec B105 — must be set via SECRET_KEY env var
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # LDAP (optionnel — laisser vide pour désactiver)
    ldap_server: str = ""
    ldap_base_dn: str = ""
    ldap_bind_dn: str = ""
    ldap_bind_password: str = ""  # nosec B105 — set via LDAP_BIND_PASSWORD env var

    # Admin local fallback (si LDAP non configuré)
    # Must be overridden via ADMIN_USERNAME / ADMIN_PASSWORD env vars in production
    admin_username: str = ""  # nosec B105 — set via ADMIN_USERNAME env var
    admin_password: str = ""  # nosec B105 — set via ADMIN_PASSWORD env var

    # Chemin monté où sont stockés les docker-compose des projets
    projects_path: str = "/projects"

    class Config:
        env_file = ".env"


settings = Settings()
