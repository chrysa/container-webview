from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.config import settings
from app.security import create_access_token
from app.security import get_current_user


router = APIRouter()

try:
    import ldap as _ldap  # type: ignore[import-untyped]

    _HAS_LDAP = True
except ImportError:
    _HAS_LDAP = False


class Token(BaseModel):
    access_token: str
    token_type: str
    username: str


def _authenticate_local(username: str, password: str) -> bool:
    return username == settings.admin_username and password == settings.admin_password


def _authenticate_ldap(username: str, password: str) -> bool:
    if not settings.ldap_server or not _HAS_LDAP:
        return False
    try:
        safe_username = _ldap.dn.escape_dn_chars(username)  # prevent LDAP injection
        conn = _ldap.initialize(settings.ldap_server)
        conn.simple_bind_s(
            f"cn={safe_username},{settings.ldap_base_dn}",
            password,
        )
        return True
    except Exception:  # noqa: BLE001 — ldap can throw many undocumented subtypes
        return False


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    authenticated = _authenticate_ldap(form_data.username, form_data.password) or _authenticate_local(
        form_data.username, form_data.password
    )
    if not authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects",
        )
    token = create_access_token({"sub": form_data.username})
    return Token(access_token=token, token_type="bearer", username=form_data.username)  # noqa: S106  # nosec B106


@router.get("/check")
def check_token(_: dict = Depends(get_current_user)) -> dict:
    return {"status": "ok"}
