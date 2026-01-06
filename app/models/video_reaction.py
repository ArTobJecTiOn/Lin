from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, func, text, Index, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ReactionType(str, Enum):
    """Типы реакций"""
    LIKE = "like"
    DISLIKE = "dislike"


class VideoReaction(Base):
    __tablename__ = "video_reactions"
    __table_args__ = (
        UniqueConstraint("user_id", "video_id", name="uq_user_video_reaction"),
        Index("idx_video_reactions_video", "video_id"),
        Index("idx_video_reactions_user", "user_id"),
        {"schema": "linap"}
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("linap.users.id"), nullable=False)
    video_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("linap.videos.id"), nullable=False)
    reaction_type: Mapped[str] = mapped_column(nullable=False)  # 'like' или 'dislike'
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
