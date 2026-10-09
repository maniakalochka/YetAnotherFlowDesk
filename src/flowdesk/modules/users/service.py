import uuid

from flowdesk.core.security import password_hasher
from flowdesk.modules.users.exceptions import UserAlreadyExistsError
from flowdesk.modules.users.models import User, UserRole
from flowdesk.modules.users.repository import UserRepository
from flowdesk.modules.users.schemas import UserRegisterSchema


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self.user_repository = repository

    async def get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        return await self.user_repository.get_by_id(user_id)

    async def get_user_by_email(self, email: str) -> User | None:
        return await self.user_repository.get_by_email(email)

    async def create_user(self, data: UserRegisterSchema) -> User:
        if await self.user_repository.get_by_email(data.email):
            raise UserAlreadyExistsError("User with this email already exists")
        user = User(
            email=data.email,
            hashed_password=password_hasher.hash(data.password),
            fname=data.fname,
            lname=data.lname,
            role=UserRole.USER,
        )
        return await self.user_repository.create(user)

    async def verify_password(self, password: str, hashed_password: str) -> bool:
        return password_hasher.verify(password, hashed_password)
