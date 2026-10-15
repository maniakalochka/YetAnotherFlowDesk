import uuid

from fastapi import APIRouter, HTTPException, status

from flowdesk.dependencies.user import CurrentAdminDep, CurrentUserDep, UserServiceDep
from flowdesk.modules.auth.service import jwt_service
from flowdesk.modules.users.exceptions import UserAlreadyExistsError
from flowdesk.modules.users.models import UserRole
from flowdesk.modules.users.schemas import (
    TokenSchema,
    UserLoginSchema,
    UserRegisterSchema,
    UserSchema,
)

user_router = APIRouter(tags=["users"])


@user_router.get("/users/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: uuid.UUID,
    current_user: CurrentUserDep,
    user_service: UserServiceDep,
) -> UserSchema:
    if current_user.id != user_id and current_user.role is not UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserSchema.model_validate(user)


@user_router.get("/users/email/{email}", response_model=UserSchema)
async def get_user_by_email(
    email: str,
    _: CurrentAdminDep,
    user_service: UserServiceDep,
) -> UserSchema:
    user = await user_service.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with email {email} not found",
        )
    return UserSchema.model_validate(user)


@user_router.post("/auth/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserRegisterSchema, user_service: UserServiceDep) -> UserSchema:
    existing_user = await user_service.get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )
    try:
        new_user = await user_service.create_user(user)
    except UserAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        ) from None
    return UserSchema.model_validate(new_user)


@user_router.post("/auth/login", response_model=TokenSchema, status_code=status.HTTP_200_OK)
async def login_user(user: UserLoginSchema, user_service: UserServiceDep) -> TokenSchema:
    existing_user = await user_service.get_user_by_email(user.email)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )
    if not existing_user.is_active or not await user_service.verify_password(
        user.password, existing_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    return TokenSchema(
        access_token=jwt_service.create_access_token(str(existing_user.id)),
        token_type="bearer",
        expires_in=jwt_service.access_token_expire_minutes * 60,
    )


@user_router.get("/auth/me", response_model=UserSchema, status_code=status.HTTP_200_OK)
async def get_current_user(current_user: CurrentUserDep) -> UserSchema:
    return UserSchema.model_validate(current_user)
