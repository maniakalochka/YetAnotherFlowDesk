from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from flowdesk.core.config import settings


class JWTService:
    def __init__(
        self,
        secret_key: str = settings.JWT_SECRET_KEY,
        algorithm: str = settings.JWT_ALGORITHM,
        access_token_expire_minutes: int = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    ) -> None:
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes

    def create_access_token(self, subject: str) -> str:
        issued_at = datetime.now(UTC)
        expire = issued_at + timedelta(minutes=self.access_token_expire_minutes)

        payload = {
            "sub": subject,
            "iat": issued_at,
            "exp": expire,
        }

        return jwt.encode(
            payload,
            self.secret_key,
            algorithm=self.algorithm,
        )

    def decode_access_token(self, token: str) -> dict[str, Any]:
        return jwt.decode(
            token,
            self.secret_key,
            algorithms=[self.algorithm],
            options={"require": ["exp", "sub"]},
        )


jwt_service = JWTService()
