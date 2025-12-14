from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database.database import get_db
from app.service.post_service import PostService

router = APIRouter(prefix="/posts")


@router.get("/{post_id}")
async def get_post(
    post_id: UUID,
    session: AsyncSession = Depends(get_db)
):
    """Получить пост по ID"""
    post_service = PostService(session)
    try:
        post = await post_service.get_post_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        return post
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/slug/{slug}")
async def get_post_by_slug(
    slug: str,
    session: AsyncSession = Depends(get_db)
):
    """Получить пост по slug"""
    post_service = PostService(session)
    try:
        post = await post_service.get_post_by_slug(slug)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        # Увеличиваем количество просмотров
        await post_service.increment_views(post.id)
        return post
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/user/{user_id}")
async def get_user_posts(
    user_id: UUID,
    skip: int = 0,
    limit: int = 20,
    session: AsyncSession = Depends(get_db)
):
    """Получить посты пользователя"""
    post_service = PostService(session)
    try:
        posts = await post_service.get_user_posts(user_id, skip, limit)
        return {"posts": posts, "count": len(posts)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/")
async def get_published_posts(
    skip: int = 0,
    limit: int = 20,
    session: AsyncSession = Depends(get_db)
):
    """Получить опубликованные посты"""
    post_service = PostService(session)
    try:
        posts = await post_service.get_published_posts(skip, limit)
        return {"posts": posts, "count": len(posts)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_post(
    owner_id: UUID,
    title: str,
    slug: str,
    content: str | None = None,
    excerpt: str | None = None,
    map_id: UUID | None = None,
    post_type: str = "post",
    session: AsyncSession = Depends(get_db)
):
    """Создать новый пост"""
    post_service = PostService(session)
    try:
        post = await post_service.create_post(
            owner_id=owner_id,
            title=title,
            slug=slug,
            content=content,
            excerpt=excerpt,
            map_id=map_id,
            post_type=post_type
        )
        return {"message": "Post created successfully", "post": post}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{post_id}")
async def update_post(
    post_id: UUID,
    title: str | None = None,
    slug: str | None = None,
    content: str | None = None,
    excerpt: str | None = None,
    session: AsyncSession = Depends(get_db)
):
    """Обновить пост"""
    post_service = PostService(session)
    try:
        update_data = {
            "title": title,
            "slug": slug,
            "content": content,
            "excerpt": excerpt
        }
        post = await post_service.update_post(post_id, update_data)
        return {"message": "Post updated successfully", "post": post}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{post_id}/publish")
async def publish_post(
    post_id: UUID,
    session: AsyncSession = Depends(get_db)
):
    """Опубликовать пост"""
    post_service = PostService(session)
    try:
        post = await post_service.publish_post(post_id)
        return {"message": "Post published successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{post_id}/unpublish")
async def unpublish_post(
    post_id: UUID,
    session: AsyncSession = Depends(get_db)
):
    """Отменить публикацию поста"""
    post_service = PostService(session)
    try:
        post = await post_service.unpublish_post(post_id)
        return {"message": "Post unpublished successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{post_id}")
async def delete_post(
    post_id: UUID,
    session: AsyncSession = Depends(get_db)
):
    """Удалить пост"""
    post_service = PostService(session)
    try:
        await post_service.delete_post(post_id)
        return {"message": "Post deleted successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
