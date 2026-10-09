from fastapi.security import HTTPBearer
from pwdlib import PasswordHash

http_bearer = HTTPBearer(auto_error=False)


class PasswordHasher:
    def __init__(self) -> None:
        self._password_hash = PasswordHash.recommended()

    def hash(self, password: str) -> str:
        return self._password_hash.hash(password)

    def verify(self, password: str, hashed_password: str) -> bool:
        return self._password_hash.verify(password, hashed_password)


password_hasher = PasswordHasher()
