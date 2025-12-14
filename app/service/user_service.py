from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
import uuid
from pathlib import Path

from app.models.user import User


class UserService:
    """Сервис для работы с пользователями"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.upload_dir = "uploads/avatars"
        Path(self.upload_dir).mkdir(parents=True, exist_ok=True)

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Получить пользователя по ID"""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalars().first()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Получить пользователя по username"""
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalars().first()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalars().first()

    async def create_user(self, username: str, email: str, display_name: Optional[str] = None) -> User:
        """Создать нового пользователя"""
        # Проверяем существует ли пользователь с таким username
        if await self.get_user_by_username(username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

        # Проверяем существует ли пользователь с таким email
        if await self.get_user_by_email(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )

        user = User(
            username=username,
            email=email,
            display_name=display_name or username
        )

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_user(self, user_id: uuid.UUID, update_data: dict) -> Optional[User]:
        """Обновить данные пользователя"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Проверяем уникальность username если он изменяется
        if "username" in update_data and update_data["username"] != user.username:
            if await self.get_user_by_username(update_data["username"]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already exists"
                )

        update_fields = {k: v for k, v in update_data.items() if v is not None}

        if not update_fields:
            return user

        for field, value in update_fields.items():
            if hasattr(user, field):
                setattr(user, field, value)

        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_avatar(self, user_id: uuid.UUID, avatar_url: str) -> User:
        """Обновить аватар пользователя"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        user.avatar_url = avatar_url
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def deactivate_user(self, user_id: uuid.UUID) -> User:
        """Деактивировать пользователя"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        user.is_active = False
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def activate_user(self, user_id: uuid.UUID) -> User:
        """Активировать пользователя"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        user.is_active = True
        await self.session.commit()
        await self.session.refresh(user)
        return user
