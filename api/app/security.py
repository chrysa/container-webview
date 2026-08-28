from datetime import UTC
from datetime import datetime
from datetime import timedelta
from typing import Annotated

from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from jose import jwt

from app.config import get_settings
from app.constants import ERR_INVALID_TOKEN
from app.constants import JWT_CLAIM_SUB
from app.constants import OAUTH2_TOKEN_URL


_oauth2_scheme = OAuth2PasswordBearer(tokenUrl=OAUTH2_TOKEN_URL)


class SecurityService:
    """Creates and validates JWT access tokens for API authentication."""

    def create_access_token(self, subject: str, expires_delta: timedelta | None = None) -> str:
        """Encode a JWT access token for *subject*."""
        settings = get_settings()
        expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
        return jwt.encode(
            {JWT_CLAIM_SUB: subject, "exp": expire},
            settings.secret_key,
            algorithm=settings.algorithm,
        )

    def get_current_user(self, token: Annotated[str, Depends(_oauth2_scheme)]) -> dict:
        """Validate bearer token and return decoded payload."""
        settings = get_settings()
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            if payload.get(JWT_CLAIM_SUB) is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=ERR_INVALID_TOKEN,
                )
            return payload
        except JWTError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERR_INVALID_TOKEN,
            ) from exc


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def verify_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide") from exc


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    return verify_token(token)
