from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database.database import get_db
from app.service.tag_service import TagService

router = APIRouter(prefix="/tags")


@router.get("/")
async def get_all_tags(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_db)
):
    """Получить все теги"""
    tag_service = TagService(session)
    try:
        tags = await tag_service.get_all_tags(skip, limit)
        return {"tags": tags, "count": len(tags)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{tag_id}")
async def get_tag(
    tag_id: UUID,
    session: AsyncSession = Depends(get_db)
):
    """Получить тег по ID"""
    tag_service = TagService(session)
    try:
        tag = await tag_service.get_tag_by_id(tag_id)
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )
        return tag
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/name/{name}")
async def get_tag_by_name(
    name: str,
    session: AsyncSession = Depends(get_db)
):
    """Получить тег по имени"""
    tag_service = TagService(session)
    try:
        tag = await tag_service.get_tag_by_name(name)
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )
        return tag
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_tag(
    name: str,
    slug: str | None = None,
    session: AsyncSession = Depends(get_db)
):
    """Создать новый тег"""
    tag_service = TagService(session)
    try:
        tag = await tag_service.create_tag(name, slug)
        return {"message": "Tag created successfully", "tag": tag}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{tag_id}")
async def update_tag(
    tag_id: UUID,
    name: str | None = None,
    slug: str | None = None,
    session: AsyncSession = Depends(get_db)
):
    """Обновить тег"""
    tag_service = TagService(session)
    try:
        update_data = {"name": name, "slug": slug}
        tag = await tag_service.update_tag(tag_id, update_data)
        return {"message": "Tag updated successfully", "tag": tag}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{tag_id}")
async def delete_tag(
    tag_id: UUID,
    session: AsyncSession = Depends(get_db)
):
    """Удалить тег"""
    tag_service = TagService(session)
    try:
        await tag_service.delete_tag(tag_id)
        return {"message": "Tag deleted successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
