from typing import Annotated

from fastapi import Depends, HTTPException
from starlette import status

from flowdesk.dependencies.user import get_current_user
from flowdesk.modules.users.models import User, UserRole


class RoleChecker:
    def __init__(self, allowed_roles: set[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: "User" = Depends(get_current_user)) -> "User":
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )
        return current_user


SupportOrAdminDep = Annotated[
    User,
    Depends(RoleChecker({UserRole.SUPPORT, UserRole.ADMIN})),
]
