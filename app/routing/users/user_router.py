from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import aiofiles
import os
from pathlib import Path

from app.core.database.database import get_db
from app.service.user_service import UserService
from app.service.auth_service import AuthService
from app.models.user import User

router = APIRouter(prefix="/users")


@router.get("/{user_id}", response_model=dict)
async def get_user(
    user_id: UUID,
    session: AsyncSession = Depends(get_db)
):
    """Получить пользователя по ID"""
    user_service = UserService(session)
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "email": user.email,
        "avatar_url": user.avatar_url,
        "is_active": user.is_active,
        "created_at": user.created_at
    }


@router.get("/username/{username}", response_model=dict)
async def get_user_by_username(
    username: str,
    session: AsyncSession = Depends(get_db)
):
    """Получить пользователя по username"""
    user_service = UserService(session)
    user = await user_service.get_user_by_username(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "email": user.email,
        "avatar_url": user.avatar_url,
        "is_active": user.is_active,
        "created_at": user.created_at
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    username: str,
    email: str,
    display_name: str | None = None,
    session: AsyncSession = Depends(get_db)
):
    """Создать нового пользователя"""
    user_service = UserService(session)
    try:
        user = await user_service.create_user(
            username=username,
            email=email,
            display_name=display_name
        )
        return {
            "message": "User created successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "display_name": user.display_name
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{user_id}")
async def update_user(
    user_id: UUID,
    username: str | None = None,
    display_name: str | None = None,
    bio: str | None = None,
    locale: str | None = None,
    timezone: str | None = None,
    current_password: str | None = None,
    new_password: str | None = None,
    session: AsyncSession = Depends(get_db)
):
    """Обновить данные пользователя"""
    user_service = UserService(session)
    try:
        # Handle password change if provided
        if new_password:
            if not current_password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password required to change password"
                )
            auth_service = AuthService(session)
            await auth_service.change_password(user_id, current_password, new_password)
        
        # Update other fields
        update_data = {
            "username": username,
            "display_name": display_name,
            "bio": bio,
            "locale": locale,
            "timezone": timezone
        }
        user = await user_service.update_user(user_id, update_data)
        return {
            "message": "User updated successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "display_name": user.display_name,
                "email": user.email
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{user_id}/avatar")
async def update_avatar(
    user_id: UUID,
    avatar_url: str,
    session: AsyncSession = Depends(get_db)
):
    """Обновить аватар пользователя"""
    user_service = UserService(session)
    try:
        user = await user_service.update_avatar(user_id, avatar_url)
        return {"message": "Avatar updated successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{user_id}/avatar")
async def upload_avatar(
    user_id: UUID,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db)
):
    """Загрузить аватар пользователя"""
    user_service = UserService(session)
    try:
        # Проверяем формат файла
        if file.content_type not in ["image/jpeg", "image/png", "image/gif", "image/webp"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only image files are allowed"
            )
        
        # Проверяем существует ли пользователь
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Создаем директорию если её нет
        upload_dir = "uploads/avatars"
        Path(upload_dir).mkdir(parents=True, exist_ok=True)
        
        # Генерируем имя файла
        file_extension = file.filename.split(".")[-1]
        filename = f"{user_id}.{file_extension}"
        filepath = os.path.join(upload_dir, filename)
        
        # Сохраняем файл
        async with aiofiles.open(filepath, "wb") as f:
            contents = await file.read()
            await f.write(contents)
        
        # Обновляем URL аватара в БД
        avatar_url = f"/uploads/avatars/{filename}"
        user = await user_service.update_avatar(user_id, avatar_url)
        
        return {
            "message": "Avatar uploaded successfully",
            "avatar_url": avatar_url
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{user_id}/deactivate")
async def deactivate_user(
    user_id: UUID,
    session: AsyncSession = Depends(get_db)
):
    """Деактивировать пользователя"""
    user_service = UserService(session)
    try:
        user = await user_service.deactivate_user(user_id)
        return {"message": "User deactivated successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{user_id}/activate")
async def activate_user(
    user_id: UUID,
    session: AsyncSession = Depends(get_db)
):
    """Активировать пользователя"""
    user_service = UserService(session)
    try:
        user = await user_service.activate_user(user_id)
        return {"message": "User activated successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
