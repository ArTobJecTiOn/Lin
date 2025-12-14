from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Integer, DateTime, func, Index, text, ForeignKey
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

LikeTarget = SAEnum("post", "video", "comment", name="like_target", schema="linap")


class Like(Base):
    __tablename__ = "likes"
    __table_args__ = (Index("idx_likes_target", "target_type", "target_id"), {"schema": "linap"})

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("linap.users.id"))
    target_type: Mapped[str] = mapped_column(LikeTarget, nullable=False)
    target_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    value: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
