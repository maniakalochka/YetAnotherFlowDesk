import uuid
from collections.abc import Generator
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from flowdesk.dependencies.user import get_current_user, get_user_service
from flowdesk.main import app
from flowdesk.modules.auth.service import jwt_service
from flowdesk.modules.users.models import User, UserRole
from flowdesk.modules.users.service import UserService


@pytest.fixture
def client() -> Generator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def make_user(*, role: UserRole = UserRole.USER, is_active: bool = True) -> User:
    return User(
        id=uuid.uuid4(),
        email="john@example.com",
        hashed_password="hashed-password",
        fname="John",
        lname="Doe",
        role=role,
        is_active=is_active,
    )


def test_login_returns_bearer_access_token(client: TestClient) -> None:
    user = make_user()
    service = AsyncMock(spec=UserService)
    service.get_user_by_email.return_value = user
    service.verify_password.return_value = True
    app.dependency_overrides[get_user_service] = lambda: service

    response = client.post(
        "/auth/login",
        json={"email": user.email, "password": "password123"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"  # noqa: S105
    assert body["expires_in"] == jwt_service.access_token_expire_minutes * 60
    assert jwt_service.decode_access_token(body["access_token"])["sub"] == str(user.id)


def test_login_rejects_inactive_user(client: TestClient) -> None:
    user = make_user(is_active=False)
    service = AsyncMock(spec=UserService)
    service.get_user_by_email.return_value = user
    app.dependency_overrides[get_user_service] = lambda: service

    response = client.post(
        "/auth/login",
        json={"email": user.email, "password": "password123"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"
    service.verify_password.assert_not_awaited()


def test_user_can_read_own_profile(client: TestClient) -> None:
    user = make_user()
    service = AsyncMock(spec=UserService)
    service.get_user_by_id.return_value = user
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_user_service] = lambda: service

    response = client.get(f"/users/{user.id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(user.id)


def test_regular_user_cannot_read_another_profile(client: TestClient) -> None:
    user = make_user()
    service = AsyncMock(spec=UserService)
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_user_service] = lambda: service

    response = client.get(f"/users/{uuid.uuid4()}")

    assert response.status_code == 403
    service.get_user_by_id.assert_not_awaited()


def test_only_admin_can_search_user_by_email(client: TestClient) -> None:
    admin = make_user(role=UserRole.ADMIN)
    found_user = make_user()
    service = AsyncMock(spec=UserService)
    service.get_user_by_email.return_value = found_user
    app.dependency_overrides[get_current_user] = lambda: admin
    app.dependency_overrides[get_user_service] = lambda: service

    response = client.get(f"/users/email/{found_user.email}")

    assert response.status_code == 200
    assert response.json()["id"] == str(found_user.id)
