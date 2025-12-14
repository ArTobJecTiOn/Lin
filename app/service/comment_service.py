from typing import Optional, List
import uuid
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.comment import Comment


class CommentService:
    """Сервис для работы с комментариями"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_comment_by_id(self, comment_id: uuid.UUID) -> Optional[Comment]:
        """Получить комментарий по ID"""
        result = await self.session.execute(
            select(Comment)
            .where(Comment.id == comment_id)
            .options(selectinload(Comment.author))
        )
        return result.scalars().first()

    async def get_post_comments(self, post_id: uuid.UUID, skip: int = 0, limit: int = 50) -> List[Comment]:
        """Получить комментарии поста"""
        result = await self.session.execute(
            select(Comment)
            .where(Comment.post_id == post_id)
            .options(selectinload(Comment.author))
            .order_by(desc(Comment.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_user_comments(self, user_id: uuid.UUID, skip: int = 0, limit: int = 50) -> List[Comment]:
        """Получить комментарии пользователя"""
        result = await self.session.execute(
            select(Comment)
            .where(Comment.author_id == user_id)
            .options(selectinload(Comment.author))
            .order_by(desc(Comment.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create_comment(
        self,
        post_id: uuid.UUID,
        author_id: uuid.UUID,
        content: str,
        parent_id: Optional[uuid.UUID] = None
    ) -> Comment:
        """Создать новый комментарий"""
        comment = Comment(
            post_id=post_id,
            author_id=author_id,
            content=content,
            parent_id=parent_id
        )

        self.session.add(comment)
        await self.session.commit()
        await self.session.refresh(comment)
        return comment

    async def update_comment(self, comment_id: uuid.UUID, content: str) -> Optional[Comment]:
        """Обновить комментарий"""
        comment = await self.get_comment_by_id(comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )

        comment.content = content
        await self.session.commit()
        await self.session.refresh(comment)
        return comment

    async def delete_comment(self, comment_id: uuid.UUID) -> bool:
        """Удалить комментарий"""
        comment = await self.get_comment_by_id(comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )

        await self.session.delete(comment)
        await self.session.commit()
        return True
