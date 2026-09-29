import uuid

from fastapi import APIRouter, HTTPException, status

from flowdesk.dependencies.user import UserServiceDep
from flowdesk.modules.users.schemas import UserCreateSchema, UserSchema

user_router = APIRouter(tags=["users"])


@user_router.get("/users/{user_id}", response_model=UserSchema)
async def get_user(user_id: uuid.UUID, user_service: UserServiceDep) -> UserSchema | None:
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserSchema.model_validate(user)


@user_router.get("/users/email/{email}", response_model=UserSchema)
async def get_user_by_email(email: str, user_service: UserServiceDep) -> UserSchema | None:
    user = await user_service.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User with email {email} not found"
        )
    return UserSchema.model_validate(user)


@user_router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreateSchema, user_service: UserServiceDep) -> UserSchema:
    existing_user = await user_service.get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists"
        )
    new_user = await user_service.create_user(user)
    return UserSchema.model_validate(new_user)
