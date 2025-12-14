from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional


class VideoCreate(BaseModel):
    title: str
    video_url: str
    description: Optional[str] = None
    thumb_url: Optional[str] = None
    map_id: Optional[UUID] = None
    agent: Optional[str] = None
    side: Optional[str] = None


class VideoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    agent: Optional[str] = None
    side: Optional[str] = None


class VideoResponse(BaseModel):
    id: UUID
    owner_id: Optional[UUID]
    title: str
    video_url: str
    description: Optional[str]
    likes: int
    dislikes: int
    views: int
    created_at: datetime

    class Config:
        from_attributes = True
