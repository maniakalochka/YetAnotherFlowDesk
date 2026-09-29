import uuid

from flowdesk.modules.users.models import User
from flowdesk.modules.users.repository import UserRepository
from flowdesk.modules.users.schemas import UserCreateSchema


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self.user_repository = repository

    async def get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        return await self.user_repository.get_by_id(user_id)

    async def get_user_by_email(self, email: str) -> User | None:
        return await self.user_repository.get_by_email(email)

    async def create_user(self, data: UserCreateSchema) -> User:
        user = User(
            email=data.email,
            hashed_password=data.hashed_password,
            fname=data.fname,
            lname=data.lname,
            role=data.role,
        )
        return await self.user_repository.create(user)
