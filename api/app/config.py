from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # LDAP (optionnel — laisser vide pour désactiver)
    ldap_server: str = ""
    ldap_base_dn: str = ""
    ldap_bind_dn: str = ""
    ldap_bind_password: str = ""

    # Admin local fallback (si LDAP non configuré)
    admin_username: str = "admin"
    admin_password: str = "admin"

    # Chemin monté où sont stockés les docker-compose des projets
    projects_path: str = "/projects"

    class Config:
        env_file = ".env"


settings = Settings()
