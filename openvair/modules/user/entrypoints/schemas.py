"""Pydantic schemas for user management and authentication.

This module defines the data schemas used for user management and authentication
in the application. It includes models for user information, user creation,
password changes, user deletion, and token management.

Schemas:
    - BaseUser: Base schema for user information.
    - UserId: Schema for representing a user ID.
    - User: Extended schema including user ID.
    - UsersList: Schema for representing a list of users.
    - UserCreate: Schema for user creation including password.
    - UserChangePassword: Schema for changing user password.
    - UserDelete: Schema for user deletion response.
    - Token: Schema for authentication tokens.
"""

from typing import List, Optional

from pydantic import EmailStr, BaseModel, ConfigDict, field_validator

from openvair.libs.validation.validators import uuid_validate


class BaseUser(BaseModel):
    """Base schema for user information.

    Attributes:
        username (str): The username of the user.
        email (Optional[EmailStr]): The email address of the user.
        is_superuser (bool): Indicates if the user is a superuser.
    """

    username: str
    email: Optional[EmailStr] = None
    is_superuser: bool


class UserId(BaseModel):
    """Schema for representing a user ID.

    Attributes:
        id (str): The unique identifier for the user.
    """

    id: str

    _normalize_id = field_validator('id')(uuid_validate)


class User(BaseUser):
    """Schema for user information including user ID.

    Attributes:
        id (str): The unique identifier for the user.

    Config:
        orm_mode (bool): Enable ORM mode for compatibility with ORMs.
    """

    id: str

    _normalize_id = field_validator('id')(uuid_validate)
    model_config = ConfigDict(from_attributes=True)


class UsersList(BaseModel):
    """Schema for representing a list of users.

    Attributes:
        users (List[Optional[User]]): A list of user objects, which may
            include None.
    """

    users: List[Optional[User]]


class UserCreate(BaseUser):
    """Schema for user creation including password.

    Attributes:
        password (str): The password for the new user.
    """

    password: str


class UserChangePassword(BaseModel):
    """Schema for changing a user's password.

    Attributes:
        new_password (str): The new password for the user.
    """

    new_password: str


class UserDelete(BaseModel):
    """Schema for user deletion response.

    Attributes:
        id (str): The unique identifier of the deleted user.
        message (str): A message indicating the result of the deletion.
    """

    id: str
    message: str

    _normalize_id = field_validator('id')(uuid_validate)


class Token(BaseModel):
    """Schema for authentication tokens.

    Attributes:
        access_token (str): The access token for user authentication.
        refresh_token (str): The refresh token used to obtain a new access
            token.
        token_type (str): The type of token, default is 'bearer'.
    """

    access_token: str
    refresh_token: str
    token_type: str = 'bearer'
