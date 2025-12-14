from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID
from typing import Optional


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    display_name: Optional[str] = None


class UserUpdate(BaseModel):
    username: Optional[str] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None
    locale: Optional[str] = None
    timezone: Optional[str] = None


class UserResponse(BaseModel):
    id: UUID
    username: str
    display_name: Optional[str]
    email: str
    bio: Optional[str]
    avatar_url: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
