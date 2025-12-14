from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database.database import get_db
from app.service.like_service import LikeService

router = APIRouter(prefix="/likes")


@router.get("/post/{post_id}")
async def get_post_likes(
    post_id: UUID,
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_db)
):
    """Получить лайки поста"""
    like_service = LikeService(session)
    try:
        likes = await like_service.get_post_likes(post_id, skip, limit)
        return {"likes": likes, "count": len(likes)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/user/{user_id}")
async def get_user_likes(
    user_id: UUID,
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_db)
):
    """Получить лайки пользователя"""
    like_service = LikeService(session)
    try:
        likes = await like_service.get_user_likes(user_id, skip, limit)
        return {"likes": likes, "count": len(likes)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/post/{post_id}")
async def like_post(
    post_id: UUID,
    user_id: UUID,
    session: AsyncSession = Depends(get_db)
):
    """Поставить лайк на пост"""
    like_service = LikeService(session)
    try:
        like = await like_service.like_post(user_id, post_id)
        return {"message": "Post liked successfully", "like": like}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/post/{post_id}")
async def unlike_post(
    post_id: UUID,
    user_id: UUID,
    session: AsyncSession = Depends(get_db)
):
    """Удалить лайк с поста"""
    like_service = LikeService(session)
    try:
        await like_service.unlike_post(user_id, post_id)
        return {"message": "Like removed successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
