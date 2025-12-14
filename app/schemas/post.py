from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional


class PostCreate(BaseModel):
    title: str
    slug: str
    content: Optional[str] = None
    excerpt: Optional[str] = None
    map_id: Optional[UUID] = None
    post_type: str = "post"


class PostUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    content: Optional[str] = None
    excerpt: Optional[str] = None


class PostResponse(BaseModel):
    id: UUID
    owner_id: Optional[UUID]
    title: str
    slug: str
    content: Optional[str]
    excerpt: Optional[str]
    published: bool
    views: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
