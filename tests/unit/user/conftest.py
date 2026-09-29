import uuid

import pytest_asyncio

from flowdesk.modules.users.models import User, UserRole


@pytest_asyncio.fixture
def user() -> User:
    return User(
        id=uuid.uuid4(),
        email="johndoe@example.com",
        hashed_password="hashedpassword",
        fname="John",
        lname="Doe",
        role=UserRole.USER,
        is_active=True,
    )
