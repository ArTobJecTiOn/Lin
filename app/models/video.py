from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, Boolean, BigInteger, Integer, DateTime, func, text, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

class Video(Base):
    __tablename__ = "videos"
    __table_args__ = (Index("idx_videos_owner", "owner_id"), {"schema": "linap"})

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("linap.users.id"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    map_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("linap.maps.id"))
    agent: Mapped[Optional[str]] = mapped_column(String(64))
    side: Mapped[Optional[str]] = mapped_column(String(16))
    video_url: Mapped[Optional[str]] = mapped_column(Text)
    thumb_url: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    views: Mapped[int] = mapped_column(BigInteger, nullable=False, server_default=text('0'))
    likes: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    dislikes: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    published: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))

    owner = relationship("User", back_populates="videos", foreign_keys=[owner_id])
