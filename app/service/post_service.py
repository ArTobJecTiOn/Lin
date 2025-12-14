from typing import Optional, List
import uuid
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.post import Post
from app.models.user import User


class PostService:
    """Сервис для работы с постами"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_post_by_id(self, post_id: uuid.UUID) -> Optional[Post]:
        """Получить пост по ID"""
        result = await self.session.execute(
            select(Post)
            .where(Post.id == post_id)
            .options(selectinload(Post.owner))
        )
        return result.scalars().first()

    async def get_post_by_slug(self, slug: str) -> Optional[Post]:
        """Получить пост по slug"""
        result = await self.session.execute(
            select(Post)
            .where(Post.slug == slug)
            .options(selectinload(Post.owner))
        )
        return result.scalars().first()

    async def get_user_posts(self, user_id: uuid.UUID, skip: int = 0, limit: int = 20) -> List[Post]:
        """Получить посты пользователя"""
        result = await self.session.execute(
            select(Post)
            .where(Post.owner_id == user_id)
            .options(selectinload(Post.owner))
            .order_by(desc(Post.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_published_posts(self, skip: int = 0, limit: int = 20) -> List[Post]:
        """Получить опубликованные посты"""
        result = await self.session.execute(
            select(Post)
            .where(Post.published == True)
            .options(selectinload(Post.owner))
            .order_by(desc(Post.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create_post(
        self,
        owner_id: uuid.UUID,
        title: str,
        slug: str,
        content: Optional[str] = None,
        excerpt: Optional[str] = None,
        map_id: Optional[uuid.UUID] = None,
        post_type: str = "post"
    ) -> Post:
        """Создать новый пост"""
        # Проверяем уникальность slug
        existing_post = await self.get_post_by_slug(slug)
        if existing_post:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Post with this slug already exists"
            )

        post = Post(
            owner_id=owner_id,
            title=title,
            slug=slug,
            content=content,
            excerpt=excerpt,
            map_id=map_id,
            type=post_type
        )

        self.session.add(post)
        await self.session.commit()
        await self.session.refresh(post)
        return post

    async def update_post(self, post_id: uuid.UUID, update_data: dict) -> Optional[Post]:
        """Обновить пост"""
        post = await self.get_post_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )

        # Проверяем уникальность нового slug если он меняется
        if "slug" in update_data and update_data["slug"] != post.slug:
            existing_post = await self.get_post_by_slug(update_data["slug"])
            if existing_post:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Post with this slug already exists"
                )

        update_fields = {k: v for k, v in update_data.items() if v is not None}

        for field, value in update_fields.items():
            if hasattr(post, field):
                setattr(post, field, value)

        await self.session.commit()
        await self.session.refresh(post)
        return post

    async def publish_post(self, post_id: uuid.UUID) -> Post:
        """Опубликовать пост"""
        post = await self.get_post_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )

        post.published = True
        await self.session.commit()
        await self.session.refresh(post)
        return post

    async def unpublish_post(self, post_id: uuid.UUID) -> Post:
        """Отменить публикацию поста"""
        post = await self.get_post_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )

        post.published = False
        await self.session.commit()
        await self.session.refresh(post)
        return post

    async def increment_views(self, post_id: uuid.UUID) -> Post:
        """Увеличить количество просмотров"""
        post = await self.get_post_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )

        post.views += 1
        await self.session.commit()
        await self.session.refresh(post)
        return post

    async def delete_post(self, post_id: uuid.UUID) -> bool:
        """Удалить пост"""
        post = await self.get_post_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )

        await self.session.delete(post)
        await self.session.commit()
        return True
