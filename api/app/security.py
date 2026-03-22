from datetime import datetime
from datetime import timedelta
from datetime import timezone
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
    def create_access_token(
        self, subject: str, expires_delta: timedelta | None = None
    ) -> str:
        """Encode a JWT access token for *subject*."""
        settings = get_settings()
        expire = datetime.now(timezone.utc) + (
            expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
        )
        return jwt.encode(
            {JWT_CLAIM_SUB: subject, "exp": expire},
            settings.secret_key,
            algorithm=settings.algorithm,
        )

    def get_current_user(
        self, token: Annotated[str, Depends(_oauth2_scheme)]
    ) -> dict:
        """Validate bearer token and return decoded payload."""
        settings = get_settings()
        try:
            payload = jwt.decode(
                token, settings.secret_key, algorithms=[settings.algorithm]
            )
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


security = SecurityService()
