"""
User-related Pydantic schemas.
"""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field, validator

from backend.schemas.base import BaseSchema


class Token(BaseModel):
    """
    Schema for JWT access token.
    """
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """
    Schema for JWT token payload.
    """
    sub: Optional[str] = None
    exp: Optional[int] = None


class UserBase(BaseSchema):
    """
    Base schema for user data.
    """
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False


class UserCreate(UserBase):
    """
    Schema for creating a new user.
    """
    email: EmailStr
    username: str
    password: str

    @validator("username")
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError("Username must be alphanumeric")
        return v


class UserUpdate(UserBase):
    """
    Schema for updating a user.
    """
    password: Optional[str] = None


class UserInDBBase(UserBase):
    """
    Base schema for a user in the database.
    """
    id: int
    created_at: datetime
    updated_at: datetime


class User(UserInDBBase):
    """
    Schema for a user.
    """
    pass


class UserInDB(UserInDBBase):
    """
    Schema for a user in the database with password hash.
    """
    hashed_password: str