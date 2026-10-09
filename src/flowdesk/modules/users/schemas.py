import uuid
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID = Field(..., description="The unique identifier of the user")
    email: EmailStr = Field(..., description="The email address of the user")
    fname: str = Field(..., description="The full name of the user")
    lname: str = Field(..., description="The last name of the user")
    role: str = Field(..., description="The role of the user (e.g.,)")
    is_active: bool = Field(..., description="Indicates if the user is active")


class UserRegisterSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    email: EmailStr = Field(..., description="The email address of the user")
    password: str = Field(..., description="The password of the user", min_length=8)
    fname: str = Field(..., description="The full name of the user")
    lname: str = Field(..., description="The last name of the user")


class UserLoginSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    email: EmailStr = Field(..., description="The email address of the user")
    password: str = Field(..., description="The password of the user", min_length=8)


class TokenSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    access_token: str = Field(..., description="The access token for the user")
    token_type: Literal["bearer"] = Field(..., description="The type of the token (e.g., Bearer)")
    expires_in: int = Field(..., description="The expiration time of the token in seconds")
