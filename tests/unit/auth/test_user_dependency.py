from unittest.mock import AsyncMock

import pytest

from flowdesk.dependencies.user import get_current_user
from flowdesk.modules.auth.exceptions import credentials_exception
from flowdesk.modules.users.service import UserService


@pytest.mark.asyncio
async def test_current_user_rejects_missing_bearer_credentials() -> None:
    user_service = AsyncMock(spec=UserService)

    with pytest.raises(type(credentials_exception)) as exc_info:
        await get_current_user(None, user_service)

    assert exc_info.value.status_code == 401
