from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Header, Form
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import aiofiles
import os
from pathlib import Path
from typing import Optional

from app.core.database.database import get_db
from app.core.security import decode_access_token
from app.service.video_service import VideoService

router = APIRouter(prefix="/videos")


def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """Получить текущего пользователя из токена"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.split(" ")[1]
    token_data = decode_access_token(token)

    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token_data


@router.get("/")
async def get_all_videos(
    skip: int = 0,
    limit: int = 20,
    published: bool = True,
    session: AsyncSession = Depends(get_db)
):
    """Получить список всех видео"""
    video_service = VideoService(session)
    try:
        # Используем метод get_user_videos с None для получения всех видео
        # Или можно создать отдельный метод в сервисе
        from sqlalchemy import select
        from app.models.video import Video
        
        query = select(Video).where(Video.published == published)
        query = query.offset(skip).limit(limit).order_by(Video.created_at.desc())
        
        result = await session.execute(query)
        videos = result.scalars().all()
        
        video_list = []
        for video in videos:
            video_dict = {
                "id": str(video.id),
                "owner_id": str(video.owner_id) if video.owner_id else None,
                "title": video.title,
                "description": video.description,
                "map_id": str(video.map_id) if video.map_id else None,
                "agent": video.agent,
                "side": video.side,
                "video_url": video.video_url,
                "thumbnail_url": video.thumb_url,
                "views": video.views,
                "likes": video.likes,
                "dislikes": video.dislikes,
                "published": video.published,
                "created_at": video.created_at.isoformat() if video.created_at else None,
                "updated_at": video.updated_at.isoformat() if video.updated_at else None
            }
            video_list.append(video_dict)
        
        return video_list
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{video_id}")
async def get_video(
    video_id: UUID,
    session: AsyncSession = Depends(get_db)
):
    """Получить видео по ID"""
    video_service = VideoService(session)
    try:
        video = await video_service.get_video_by_id(video_id)
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found"
            )
        await video_service.increment_views(video_id)
        return video
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/user/{user_id}")
async def get_user_videos(
    user_id: UUID,
    skip: int = 0,
    limit: int = 20,
    session: AsyncSession = Depends(get_db)
):
    """Получить видео пользователя"""
    video_service = VideoService(session)
    try:
        videos = await video_service.get_user_videos(user_id, skip, limit)
        return {"videos": videos, "count": len(videos)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/agent/{agent}")
async def get_videos_by_agent(
    agent: str,
    skip: int = 0,
    limit: int = 20,
    session: AsyncSession = Depends(get_db)
):
    """Получить видео по агенту"""
    video_service = VideoService(session)
    try:
        videos = await video_service.get_videos_by_agent(agent, skip, limit)
        return {"videos": videos, "count": len(videos)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/map/{map_id}")
async def get_videos_by_map(
    map_id: UUID,
    skip: int = 0,
    limit: int = 20,
    session: AsyncSession = Depends(get_db)
):
    """Получить видео по карте"""
    video_service = VideoService(session)
    try:
        videos = await video_service.get_videos_by_map(map_id, skip, limit)
        return {"videos": videos, "count": len(videos)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_video(
    owner_id: UUID,
    title: str,
    video_url: str,
    description: str | None = None,
    thumb_url: str | None = None,
    map_id: UUID | None = None,
    agent: str | None = None,
    side: str | None = None,
    session: AsyncSession = Depends(get_db)
):
    """Создать новое видео"""
    video_service = VideoService(session)
    try:
        video = await video_service.create_video(
            owner_id=owner_id,
            title=title,
            video_url=video_url,
            description=description,
            thumb_url=thumb_url,
            map_id=map_id,
            agent=agent,
            side=side
        )
        return {"message": "Video created successfully", "video": video}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{video_id}")
async def update_video(
    video_id: UUID,
    title: str | None = None,
    description: str | None = None,
    agent: str | None = None,
    side: str | None = None,
    session: AsyncSession = Depends(get_db)
):
    """Обновить видео"""
    video_service = VideoService(session)
    try:
        update_data = {
            "title": title,
            "description": description,
            "agent": agent,
            "side": side
        }
        video = await video_service.update_video(video_id, update_data)
        return {"message": "Video updated successfully", "video": video}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{video_id}/like")
async def like_video(
    video_id: UUID,
    session: AsyncSession = Depends(get_db)
):
    """Добавить лайк к видео"""
    video_service = VideoService(session)
    try:
        video = await video_service.like_video(video_id)
        return {"message": "Video liked successfully", "likes": video.likes}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{video_id}/dislike")
async def dislike_video(
    video_id: UUID,
    session: AsyncSession = Depends(get_db)
):
    """Добавить дизлайк к видео"""
    video_service = VideoService(session)
    try:
        video = await video_service.dislike_video(video_id)
        return {"message": "Video disliked successfully", "dislikes": video.dislikes}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/upload")
async def upload_video(
    title: str = Form(...),
    file: UploadFile = File(...),
    description: str | None = Form(None),
    agent: str | None = Form(None),
    side: str | None = Form(None),
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Загрузить видео файл"""
    video_service = VideoService(session)
    try:
        print(f"[VIDEO UPLOAD] Received upload request: title={title}, agent={agent}, side={side}, user={current_user}")
        
        # Get owner_id from current user (TokenData object)
        owner_id = UUID(current_user.user_id)
        
        # Проверяем формат файла
        if file.content_type not in ["video/mp4", "video/quicktime", "application/octet-stream"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only MP4 video files are allowed. Received: {file.content_type}"
            )
        
        # Создаем директорию для видео если её нет
        upload_dir = "uploads/videos"
        Path(upload_dir).mkdir(parents=True, exist_ok=True)
        
        # Генерируем имя файла
        file_extension = file.filename.split(".")[-1] if file.filename else "mp4"
        unique_id = os.urandom(8).hex()
        filename = f"{title.replace(' ', '_')}_{unique_id}.{file_extension}"
        filepath = os.path.join(upload_dir, filename)
        
        # Сохраняем файл
        async with aiofiles.open(filepath, "wb") as f:
            contents = await file.read()
            await f.write(contents)
        
        # Создаем видео в БД
        video_url = f"/uploads/videos/{filename}"
        video = await video_service.create_video(
            owner_id=owner_id,
            title=title,
            video_url=video_url,
            description=description,
            agent=agent,
            side=side
        )
        
        print(f"[VIDEO UPLOAD] Video created: {video}")
        
        return {
            "message": "Video uploaded successfully",
            "video": video,
            "video_url": video_url
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"[VIDEO UPLOAD] Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{video_id}")
async def delete_video(
    video_id: UUID,
    session: AsyncSession = Depends(get_db)
):
    """Удалить видео"""
    video_service = VideoService(session)
    try:
        await video_service.delete_video(video_id)
        return {"message": "Video deleted successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
