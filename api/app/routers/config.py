from fastapi import APIRouter
from pydantic import BaseModel

from app.config import settings


router = APIRouter()


class ConfigStatus(BaseModel):
    """Public, non-sensitive runtime configuration flags."""

    demo_mode: bool
    ldap_enabled: bool


@router.get("/status", response_model=ConfigStatus)
def get_config_status() -> ConfigStatus:
    """Report runtime flags the frontend needs (no secrets exposed).

    Public on purpose: the demo banner and the login page read it before any
    authentication so a visitor knows demo credentials are available.
    """
    return ConfigStatus(
        demo_mode=settings.demo_mode,
        ldap_enabled=bool(settings.ldap_server),
    )
