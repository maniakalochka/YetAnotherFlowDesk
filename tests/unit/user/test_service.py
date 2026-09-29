from unittest.mock import AsyncMock

import pytest

from flowdesk.modules.users.models import User, UserRole
from flowdesk.modules.users.repository import UserRepository
from flowdesk.modules.users.schemas import UserCreateSchema
from flowdesk.modules.users.service import UserService


@pytest.mark.asyncio
async def test_user_service_can_return_user_by_id(user: User) -> None:
    # Arrange
    repository = AsyncMock(spec=UserRepository)
    repository.get_by_id.return_value = user
    user_service = UserService(repository=repository)
    # Act
    result = await user_service.get_user_by_id(user.id)
    # Assert
    assert result is user

    repository.get_by_id.assert_awaited_once_with(user.id)


@pytest.mark.asyncio
async def test_user_service_returns_none_for_nonexistent_user_id() -> None:
    # Arrange
    repository = AsyncMock(spec=UserRepository)
    repository.get_by_id.return_value = None
    user_service = UserService(repository=repository)
    non_existent_user_id = "non-existent-id"
    # Act
    result = await user_service.get_user_by_id(non_existent_user_id)  # type: ignore
    # Assert
    assert result is None

    repository.get_by_id.assert_awaited_once_with(non_existent_user_id)


@pytest.mark.asyncio
async def test_user_service_returns_none_for_nonexistent_user_email() -> None:
    # Arrange
    repository = AsyncMock(spec=UserRepository)
    repository.get_by_email.return_value = None
    user_service = UserService(repository=repository)
    non_existent_user_email = "non-existent-email@example.com"
    # Act
    result = await user_service.get_user_by_email(non_existent_user_email)
    # Assert
    assert result is None

    repository.get_by_email.assert_awaited_once_with(non_existent_user_email)


@pytest.mark.asyncio
async def test_user_service_can_return_user_by_email(user: User) -> None:
    # Arrange
    repository = AsyncMock(spec=UserRepository)
    repository.get_by_email.return_value = user
    user_service = UserService(repository=repository)
    # Act
    result = await user_service.get_user_by_email(user.email)
    # Assert
    assert result is user

    repository.get_by_email.assert_awaited_once_with(user.email)


@pytest.mark.asyncio
async def test_user_service_can_create_user() -> None:
    # Arrange
    repository = AsyncMock(spec=UserRepository)

    data = UserCreateSchema(
        email="john@example.com",
        hashed_password="password123",
        fname="John",
        lname="Doe",
        role=UserRole.USER,
    )

    saved_user = User(
        email=data.email,
        hashed_password="hashed_password",
        fname=data.fname,
        lname=data.lname,
        role=data.role,
    )

    repository.create.return_value = saved_user

    service = UserService(repository=repository)

    # Act
    result = await service.create_user(data)

    # Assert
    assert result is saved_user

    repository.create.assert_awaited_once()

    created_user = repository.create.await_args.args[0]

    assert isinstance(created_user, User)
    assert created_user.email == data.email
    assert created_user.fname == data.fname
    assert created_user.lname == data.lname


@pytest.mark.asyncio
async def test_user_service_create_user_raises_exception_on_failure(user: User) -> None:
    # Arrange
    repository = AsyncMock(spec=UserRepository)
    repository.create.side_effect = Exception("Database error")
    user_service = UserService(repository=repository)
    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await user_service.create_user(user)

    assert str(exc_info.value) == "Database error"
