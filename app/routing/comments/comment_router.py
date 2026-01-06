from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from pydantic import BaseModel
from typing import Optional

from app.core.database.database import get_db
from app.service.comment_service import CommentService
from app.routing.videos.video_router import get_current_user
from app.models.comment import Comment

router = APIRouter(prefix="/comments")

class CommentCreate(BaseModel):
    content: str
    video_id: Optional[UUID] = None
    post_id: Optional[UUID] = None
    parent_id: Optional[UUID] = None


@router.get("/{comment_id}")
async def get_comment(
    comment_id: UUID,
    session: AsyncSession = Depends(get_db)
):
    """Получить комментарий по ID"""
    comment_service = CommentService(session)
    try:
        comment = await comment_service.get_comment_by_id(comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        return comment
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/post/{post_id}")
async def get_post_comments(
    post_id: UUID,
    skip: int = 0,
    limit: int = 50,
    session: AsyncSession = Depends(get_db)
):
    """Получить комментарии поста"""
    comment_service = CommentService(session)
    try:
        comments = await comment_service.get_post_comments(post_id, skip, limit)
        return {"comments": comments, "count": len(comments)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/user/{user_id}")
async def get_user_comments(
    user_id: UUID,
    skip: int = 0,
    limit: int = 50,
    session: AsyncSession = Depends(get_db)
):
    """Получить комментарии пользователя"""
    comment_service = CommentService(session)
    try:
        comments = await comment_service.get_user_comments(user_id, skip, limit)
        return comments
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/video/{video_id}")
async def get_video_comments(
    video_id: UUID,
    skip: int = 0,
    limit: int = 50,
    session: AsyncSession = Depends(get_db)
):
    """Получить комментарии видео"""
    print(f"[COMMENTS] Getting comments for video {video_id}")
    comment_service = CommentService(session)
    try:
        comments = await comment_service.get_video_comments(video_id, skip, limit)
        print(f"[COMMENTS] Found {len(comments)} comments")
        return comments
    except Exception as e:
        print(f"[COMMENTS] Exception: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment_data: CommentCreate,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Создать новый комментарий"""
    print(f"[COMMENTS] Creating comment from user {current_user} with data: {comment_data}")
    comment_service = CommentService(session)
    try:
        comment = await comment_service.create_comment(
            author_id=current_user.user_id,
            content=comment_data.content,
            video_id=comment_data.video_id,
            post_id=comment_data.post_id,
            parent_id=comment_data.parent_id
        )
        print(f"[COMMENTS] Comment created successfully: {comment.id}")
        return comment
    except HTTPException as e:
        print(f"[COMMENTS] HTTPException: {e}")
        raise e
    except Exception as e:
        print(f"[COMMENTS] Exception: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{comment_id}")
async def update_comment(
    comment_id: UUID,
    content: str,
    session: AsyncSession = Depends(get_db)
):
    """Обновить комментарий"""
    comment_service = CommentService(session)
    try:
        comment = await comment_service.update_comment(comment_id, content)
        return {"message": "Comment updated successfully", "comment": comment}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: UUID,
    session: AsyncSession = Depends(get_db)
):
    """Удалить комментарий"""
    comment_service = CommentService(session)
    try:
        await comment_service.delete_comment(comment_id)
        return {"message": "Comment deleted successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
