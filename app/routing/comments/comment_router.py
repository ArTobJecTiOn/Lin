from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database.database import get_db
from app.service.comment_service import CommentService

router = APIRouter(prefix="/comments")


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
        return {"comments": comments, "count": len(comments)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: UUID,
    author_id: UUID,
    content: str,
    parent_id: UUID | None = None,
    session: AsyncSession = Depends(get_db)
):
    """Создать новый комментарий"""
    comment_service = CommentService(session)
    try:
        comment = await comment_service.create_comment(
            post_id=post_id,
            author_id=author_id,
            content=content,
            parent_id=parent_id
        )
        return {"message": "Comment created successfully", "comment": comment}
    except Exception as e:
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
