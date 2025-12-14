from __future__ import annotations

import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class PostTag(Base):
    __tablename__ = "post_tags"
    __table_args__ = ({"schema": "linap"},)

    post_id: Mapped["uuid.UUID"] = mapped_column(UUID(as_uuid=True), ForeignKey("linap.posts.id"), primary_key=True)
    tag_id: Mapped["uuid.UUID"] = mapped_column(UUID(as_uuid=True), ForeignKey("linap.tags.id"), primary_key=True)
