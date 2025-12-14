from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Text, DateTime, Boolean, func, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class PasswordReset(Base):
    __tablename__ = "password_resets"
    __table_args__ = ({"schema": "linap"},)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("linap.users.id"))
    token: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    used: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
