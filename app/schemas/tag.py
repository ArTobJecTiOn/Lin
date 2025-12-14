from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class TagCreate(BaseModel):
    name: str
    slug: Optional[str] = None


class TagUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None


class TagResponse(BaseModel):
    id: UUID
    name: str
    slug: str

    class Config:
        from_attributes = True
