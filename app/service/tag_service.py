from typing import Optional, List
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.tag import Tag


class TagService:
    """Сервис для работы с тегами"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_tag_by_id(self, tag_id: uuid.UUID) -> Optional[Tag]:
        """Получить тег по ID"""
        result = await self.session.execute(
            select(Tag).where(Tag.id == tag_id)
        )
        return result.scalars().first()

    async def get_tag_by_name(self, name: str) -> Optional[Tag]:
        """Получить тег по имени"""
        result = await self.session.execute(
            select(Tag).where(Tag.name == name)
        )
        return result.scalars().first()

    async def get_all_tags(self, skip: int = 0, limit: int = 100) -> List[Tag]:
        """Получить все теги"""
        result = await self.session.execute(
            select(Tag).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def create_tag(self, name: str, slug: Optional[str] = None) -> Tag:
        """Создать новый тег"""
        # Проверяем уникальность имени
        existing_tag = await self.get_tag_by_name(name)
        if existing_tag:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tag with this name already exists"
            )

        tag = Tag(name=name, slug=slug or name.lower().replace(" ", "-"))

        self.session.add(tag)
        await self.session.commit()
        await self.session.refresh(tag)
        return tag

    async def update_tag(self, tag_id: uuid.UUID, update_data: dict) -> Optional[Tag]:
        """Обновить тег"""
        tag = await self.get_tag_by_id(tag_id)
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )

        # Проверяем уникальность имени если оно меняется
        if "name" in update_data and update_data["name"] != tag.name:
            existing_tag = await self.get_tag_by_name(update_data["name"])
            if existing_tag:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Tag with this name already exists"
                )

        update_fields = {k: v for k, v in update_data.items() if v is not None}

        for field, value in update_fields.items():
            if hasattr(tag, field):
                setattr(tag, field, value)

        await self.session.commit()
        await self.session.refresh(tag)
        return tag

    async def delete_tag(self, tag_id: uuid.UUID) -> bool:
        """Удалить тег"""
        tag = await self.get_tag_by_id(tag_id)
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )

        await self.session.delete(tag)
        await self.session.commit()
        return True
