from typing import Optional, List
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.like import Like


class LikeService:
    """Сервис для работы с лайками"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_like_by_id(self, like_id: uuid.UUID) -> Optional[Like]:
        """Получить лайк по ID"""
        result = await self.session.execute(
            select(Like)
            .where(Like.id == like_id)
            .options(selectinload(Like.user))
        )
        return result.scalars().first()

    async def get_user_likes(self, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Like]:
        """Получить лайки пользователя"""
        result = await self.session.execute(
            select(Like)
            .where(Like.user_id == user_id)
            .options(selectinload(Like.user))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_post_likes(self, post_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Like]:
        """Получить лайки поста"""
        result = await self.session.execute(
            select(Like)
            .where(Like.post_id == post_id)
            .options(selectinload(Like.user))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def like_post(self, user_id: uuid.UUID, post_id: uuid.UUID) -> Like:
        """Поставить лайк на пост"""
        # Проверяем, не лайкнул ли уже пользователь этот пост
        existing_like = await self.session.execute(
            select(Like)
            .where(Like.user_id == user_id)
            .where(Like.post_id == post_id)
        )
        if existing_like.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already liked this post"
            )

        like = Like(user_id=user_id, post_id=post_id)

        self.session.add(like)
        await self.session.commit()
        await self.session.refresh(like)
        return like

    async def unlike_post(self, user_id: uuid.UUID, post_id: uuid.UUID) -> bool:
        """Удалить лайк с поста"""
        result = await self.session.execute(
            select(Like)
            .where(Like.user_id == user_id)
            .where(Like.post_id == post_id)
        )
        like = result.scalars().first()

        if not like:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Like not found"
            )

        await self.session.delete(like)
        await self.session.commit()
        return True

    async def delete_like(self, like_id: uuid.UUID) -> bool:
        """Удалить лайк"""
        like = await self.get_like_by_id(like_id)
        if not like:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Like not found"
            )

        await self.session.delete(like)
        await self.session.commit()
        return True
