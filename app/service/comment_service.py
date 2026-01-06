from typing import Optional, List
import uuid
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
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
            .options(joinedload(Comment.author))
        )
        return result.unique().scalars().first()

    async def get_post_comments(self, post_id: uuid.UUID, skip: int = 0, limit: int = 50) -> List[Comment]:
        """Получить комментарии поста"""
        result = await self.session.execute(
            select(Comment)
            .where(Comment.post_id == post_id)
            .options(joinedload(Comment.author))
            .order_by(desc(Comment.created_at))
            .offset(skip)
            .limit(limit)
        )
        return list(result.unique().scalars().all())

    async def get_user_comments(self, user_id: uuid.UUID, skip: int = 0, limit: int = 50) -> List[Comment]:
        """Получить комментарии пользователя"""
        result = await self.session.execute(
            select(Comment)
            .where(Comment.user_id == user_id)
            .options(joinedload(Comment.author))
            .order_by(desc(Comment.created_at))
            .offset(skip)
            .limit(limit)
        )
        return list(result.unique().scalars().all())

    async def get_video_comments(self, video_id: uuid.UUID, skip: int = 0, limit: int = 50) -> List[Comment]:
        """Получить комментарии видео"""
        result = await self.session.execute(
            select(Comment)
            .where(Comment.video_id == video_id)
            .options(joinedload(Comment.author))
            .order_by(desc(Comment.created_at))
            .offset(skip)
            .limit(limit)
        )
        comments = list(result.unique().scalars().all())
        print(f"[COMMENT SERVICE] Found {len(comments)} comments for video {video_id}")
        for comment in comments:
            print(f"  - Comment {comment.id}: author_id={comment.author_id}, author={comment.author}")
        return comments

    async def create_comment(
        self,
        author_id: uuid.UUID,
        content: str,
        post_id: Optional[uuid.UUID] = None,
        video_id: Optional[uuid.UUID] = None,
        parent_id: Optional[uuid.UUID] = None
    ) -> Comment:
        """Создать новый комментарий"""
        if not post_id and not video_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either post_id or video_id must be provided"
            )
        
        comment = Comment(
            post_id=post_id,
            video_id=video_id,
            user_id=author_id,
            content=content,
            parent_id=parent_id
        )

        self.session.add(comment)
        await self.session.commit()
        await self.session.refresh(comment)
        # Reload author relationship
        await self.session.refresh(comment, ["author"])
        print(f"[COMMENT SERVICE] Comment created with author: {comment.author}")
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
