from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends
from pydantic import BaseModel

from app.config import settings
from app.security import create_access_token

router = APIRouter()


class Token(BaseModel):
    access_token: str
    token_type: str
    username: str


def _authenticate_local(username: str, password: str) -> bool:
    return username == settings.admin_username and password == settings.admin_password


def _authenticate_ldap(username: str, password: str) -> bool:
    if not settings.ldap_server:
        return False
    try:
        import ldap  # type: ignore
        conn = ldap.initialize(settings.ldap_server)
        conn.simple_bind_s(
            f"cn={username},{settings.ldap_base_dn}",
            password,
        )
        return True
    except Exception:
        return False


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    authenticated = _authenticate_ldap(form_data.username, form_data.password) or \
                    _authenticate_local(form_data.username, form_data.password)
    if not authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects",
        )
    token = create_access_token({"sub": form_data.username})
    return Token(access_token=token, token_type="bearer", username=form_data.username)


@router.get("/check")
def check_token(payload: dict = Depends(lambda: None)):
    # Vérifié côté middleware OAuth2 — si on arrive ici le token est valide
    return {"status": "ok"}
