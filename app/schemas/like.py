from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class LikeResponse(BaseModel):
    id: UUID
    user_id: UUID
    post_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
