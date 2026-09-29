import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from flowdesk.modules.users.models import UserRole


class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID = Field(..., description="The unique identifier of the user")
    email: EmailStr = Field(..., description="The email address of the user")
    fname: str = Field(..., description="The full name of the user")
    lname: str = Field(..., description="The last name of the user")
    role: str = Field(..., description="The role of the user (e.g.,)")
    is_active: bool = Field(..., description="Indicates if the user is active")


class UserCreateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    email: EmailStr = Field(..., description="The email address of the user")
    hashed_password: str = Field(..., description="The password of the user")
    fname: str = Field(..., description="The full name of the user")
    lname: str = Field(..., description="The last name of the user")
    role: UserRole = Field(..., description="The role of the user (e.g.,)")
