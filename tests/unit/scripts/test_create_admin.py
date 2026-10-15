from unittest.mock import AsyncMock

import pytest

from flowdesk.core.security import password_hasher
from flowdesk.modules.users.models import User, UserRole
from flowdesk.modules.users.repository import UserRepository
from flowdesk.modules.users.schemas import UserRegisterSchema
from flowdesk.scripts.create_admin import (
    ADMIN_PASSWORD_ENV,
    AdminProvisionStatus,
    ExistingUserNotAdminError,
    PasswordConfirmationError,
    ensure_admin,
    read_password,
)


def make_data() -> UserRegisterSchema:
    return UserRegisterSchema(
        email="admin@example.com",
        password="password123",
        fname="Admin",
        lname="User",
    )


def make_user(role: UserRole = UserRole.USER) -> User:
    return User(
        email="admin@example.com",
        hashed_password="existing-hash",
        fname="Admin",
        lname="User",
        role=role,
        is_active=True,
        is_verified=role is UserRole.ADMIN,
    )


@pytest.mark.asyncio
async def test_ensure_admin_creates_verified_admin_with_hashed_password() -> None:
    repository = AsyncMock(spec=UserRepository)
    repository.get_by_email.return_value = None
    repository.create.side_effect = lambda user: user

    admin, result = await ensure_admin(repository, make_data())

    assert result is AdminProvisionStatus.CREATED
    assert admin.role is UserRole.ADMIN
    assert admin.is_active is True
    assert admin.is_verified is True
    assert admin.hashed_password != "password123"  # noqa: S105
    assert password_hasher.verify("password123", admin.hashed_password)
    repository.create.assert_awaited_once_with(admin)
    repository.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_ensure_admin_is_idempotent_for_existing_admin() -> None:
    existing_admin = make_user(UserRole.ADMIN)
    repository = AsyncMock(spec=UserRepository)
    repository.get_by_email.return_value = existing_admin

    admin, result = await ensure_admin(repository, make_data())

    assert admin is existing_admin
    assert result is AdminProvisionStatus.ALREADY_ADMIN
    repository.create.assert_not_awaited()
    repository.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_ensure_admin_refuses_implicit_promotion() -> None:
    repository = AsyncMock(spec=UserRepository)
    repository.get_by_email.return_value = make_user()

    with pytest.raises(ExistingUserNotAdminError):
        await ensure_admin(repository, make_data())

    repository.create.assert_not_awaited()
    repository.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_ensure_admin_promotes_and_activates_existing_user_explicitly() -> None:
    existing_user = make_user()
    existing_user.fname = "Old"
    existing_user.lname = "Name"
    existing_user.is_active = False
    repository = AsyncMock(spec=UserRepository)
    repository.get_by_email.return_value = existing_user
    repository.save.side_effect = lambda user: user

    admin, result = await ensure_admin(
        repository,
        make_data(),
        promote_existing=True,
    )

    assert admin is existing_user
    assert result is AdminProvisionStatus.PROMOTED
    assert admin.role is UserRole.ADMIN
    assert admin.is_active is True
    assert admin.is_verified is True
    assert admin.fname == "Admin"
    assert admin.lname == "User"
    assert password_hasher.verify("password123", admin.hashed_password)
    repository.save.assert_awaited_once_with(existing_user)
    repository.create.assert_not_awaited()


def test_read_password_uses_environment_without_prompt(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(ADMIN_PASSWORD_ENV, "password123")
    prompt = AsyncMock()
    monkeypatch.setattr("flowdesk.scripts.create_admin.getpass.getpass", prompt)

    assert read_password() == "password123"
    prompt.assert_not_called()


def test_read_password_rejects_mismatched_confirmation(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(ADMIN_PASSWORD_ENV, raising=False)
    prompts = iter(["password123", "different-password"])
    monkeypatch.setattr(
        "flowdesk.scripts.create_admin.getpass.getpass",
        lambda _: next(prompts),
    )

    with pytest.raises(PasswordConfirmationError):
        read_password()
