from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.constants import ERR_INVALID_CREDENTIALS, TOKEN_TYPE_BEARER
from app.security import security
from app.services.auth_service import auth_service

router = APIRouter()


class Token(BaseModel):
    access_token: str
    token_type: str
    username: str


@router.post("/login")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    if not auth_service.authenticate(form_data.username, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERR_INVALID_CREDENTIALS,
        )
    return Token(
        access_token=security.create_access_token(form_data.username),
        token_type=TOKEN_TYPE_BEARER,
        username=form_data.username,
    )


@router.get("/check")
def check_token(_: Annotated[dict, Depends(security.get_current_user)]) -> dict:
    return {"status": "ok"}
