from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from flowdesk.core.security import http_bearer
from flowdesk.dependencies.database import get_async_session
from flowdesk.modules.auth.exceptions import credentials_exception
from flowdesk.modules.auth.service import jwt_service
from flowdesk.modules.users.models import User, UserRole
from flowdesk.modules.users.repository import UserRepository
from flowdesk.modules.users.service import UserService


def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UserRepository:
    return UserRepository(session)


def get_user_service(
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    return UserService(repository)


async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(http_bearer),
    ],
    user_service: Annotated[
        UserService,
        Depends(get_user_service),
    ],
) -> User:
    if credentials is None:
        raise credentials_exception
    try:
        payload = jwt_service.decode_access_token(credentials.credentials)
        sub = payload.get("sub")
        if sub is None:
            raise credentials_exception
        user_id = UUID(sub)

    except (jwt.InvalidTokenError, ValueError):
        raise credentials_exception from None

    user = await user_service.get_user_by_id(user_id)

    if user is None or not user.is_active:
        raise credentials_exception
    return user


UserServiceDep = Annotated[UserService, Depends(get_user_service)]

CurrentUserDep = Annotated[
    User,
    Depends(get_current_user),
]


def require_admin(current_user: CurrentUserDep) -> User:
    if current_user.role is not UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    return current_user


CurrentAdminDep = Annotated[
    User,
    Depends(require_admin),
]
