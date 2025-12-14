from typing import Optional, List
import uuid
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.video import Video


class VideoService:
    """Сервис для работы с видео"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.upload_dir = "uploads/videos"

    async def get_video_by_id(self, video_id: uuid.UUID) -> Optional[Video]:
        """Получить видео по ID"""
        result = await self.session.execute(
            select(Video)
            .where(Video.id == video_id)
            .options(selectinload(Video.owner))
        )
        return result.scalars().first()

    async def get_user_videos(self, user_id: uuid.UUID, skip: int = 0, limit: int = 20) -> List[Video]:
        """Получить видео пользователя"""
        result = await self.session.execute(
            select(Video)
            .where(Video.owner_id == user_id)
            .options(selectinload(Video.owner))
            .order_by(desc(Video.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_videos_by_agent(self, agent: str, skip: int = 0, limit: int = 20) -> List[Video]:
        """Получить видео по агенту"""
        result = await self.session.execute(
            select(Video)
            .where(Video.agent == agent)
            .options(selectinload(Video.owner))
            .order_by(desc(Video.views))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_videos_by_map(self, map_id: uuid.UUID, skip: int = 0, limit: int = 20) -> List[Video]:
        """Получить видео по карте"""
        result = await self.session.execute(
            select(Video)
            .where(Video.map_id == map_id)
            .options(selectinload(Video.owner))
            .order_by(desc(Video.views))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create_video(
        self,
        owner_id: uuid.UUID,
        title: str,
        video_url: str,
        description: Optional[str] = None,
        thumb_url: Optional[str] = None,
        map_id: Optional[uuid.UUID] = None,
        agent: Optional[str] = None,
        side: Optional[str] = None
    ) -> Video:
        """Создать новое видео"""
        video = Video(
            owner_id=owner_id,
            title=title,
            video_url=video_url,
            description=description,
            thumb_url=thumb_url,
            map_id=map_id,
            agent=agent,
            side=side
        )

        self.session.add(video)
        await self.session.commit()
        await self.session.refresh(video)
        return video

    async def update_video(self, video_id: uuid.UUID, update_data: dict) -> Optional[Video]:
        """Обновить видео"""
        video = await self.get_video_by_id(video_id)
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found"
            )

        update_fields = {k: v for k, v in update_data.items() if v is not None}

        for field, value in update_fields.items():
            if hasattr(video, field):
                setattr(video, field, value)

        await self.session.commit()
        await self.session.refresh(video)
        return video

    async def increment_views(self, video_id: uuid.UUID) -> Video:
        """Увеличить количество просмотров"""
        video = await self.get_video_by_id(video_id)
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found"
            )

        video.views += 1
        await self.session.commit()
        await self.session.refresh(video)
        return video

    async def like_video(self, video_id: uuid.UUID) -> Video:
        """Добавить лайк к видео"""
        video = await self.get_video_by_id(video_id)
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found"
            )

        video.likes += 1
        await self.session.commit()
        await self.session.refresh(video)
        return video

    async def dislike_video(self, video_id: uuid.UUID) -> Video:
        """Добавить дизлайк к видео"""
        video = await self.get_video_by_id(video_id)
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found"
            )

        video.dislikes += 1
        await self.session.commit()
        await self.session.refresh(video)
        return video

    async def delete_video(self, video_id: uuid.UUID) -> bool:
        """Удалить видео"""
        video = await self.get_video_by_id(video_id)
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found"
            )

        await self.session.delete(video)
        await self.session.commit()
        return True
