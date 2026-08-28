from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.constants import ERR_INVALID_CREDENTIALS
from app.constants import TokenType
from app.security import security
from app.services.auth_service import auth_service


router = APIRouter()

try:
    import ldap as _ldap

    _HAS_LDAP = True
except ImportError:
    _HAS_LDAP = False


class Token(BaseModel):
    """OAuth2 token response payload."""

    access_token: str
    token_type: str
    username: str


@router.post("/login", response_model=Token)  # fastapi-missing-links: disable
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    """Authenticate a user and return a JWT bearer token."""
    if not auth_service.authenticate(form_data.username, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects",
        )
    token = create_access_token({"sub": form_data.username})
    return Token(access_token=token, token_type="bearer", username=form_data.username)  # noqa: S106  # nosec B106


@router.get("/check", response_model=dict)
def check_token(_: Annotated[dict, Depends(security.get_current_user)]) -> dict:
    """Validate the current bearer token and return a confirmation payload."""
    return {"status": "ok"}
