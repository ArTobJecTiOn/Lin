from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import String, Text, Boolean, BigInteger, DateTime, func, text, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, foreign

from .base import Base




class Post(Base):
    __tablename__ = "posts"
    __table_args__ = (Index("idx_posts_owner", "owner_id"), {"schema": "linap"})

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("linap.users.id"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    excerpt: Mapped[Optional[str]] = mapped_column(Text)
    content: Mapped[Optional[str]] = mapped_column(Text)
    type: Mapped[str] = mapped_column(String(32), nullable=False, server_default=text("'post'"))
    map_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("linap.maps.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    published: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    views: Mapped[int] = mapped_column(BigInteger, nullable=False, server_default=text('0'))

    owner = relationship("User", back_populates="posts", foreign_keys=[owner_id])
    tags: Mapped[List["Tag"]] = relationship("Tag", secondary="linap.post_tags", viewonly=True)
