from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional

from app.core.database.database import get_db
from app.core.security import decode_access_token
from app.service.auth_service import AuthService
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    ChangePasswordRequest,
    ErrorResponse
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


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


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    session: AsyncSession = Depends(get_db)
):
    """Регистрация нового пользователя"""
    try:
        auth_service = AuthService(session)
        user = await auth_service.register(
            username=request.username,
            email=request.email,
            password=request.password,
            display_name=request.display_name
        )

        # Создаем токен
        token = auth_service.create_access_token(user.id, user.username)

        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user_id=user.id,
            username=user.username,
            expires_in=86400  # 24 hours
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(get_db)
):
    """Вход в систему"""
    try:
        auth_service = AuthService(session)
        user = await auth_service.authenticate(
            username=request.username,
            password=request.password
        )

        # Создаем токен
        token = auth_service.create_access_token(user.id, user.username)

        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user_id=user.id,
            username=user.username,
            expires_in=86400  # 24 hours
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    token_data: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Изменить пароль"""
    try:
        auth_service = AuthService(session)
        user_id = UUID(token_data.user_id)

        await auth_service.change_password(
            user_id=user_id,
            old_password=request.old_password,
            new_password=request.new_password
        )

        return {"message": "Password changed successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/me")
async def get_current_user_info(
    token_data: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Получить информацию о текущем пользователе"""
    from app.service.user_service import UserService
    
    user_service = UserService(session)
    user = await user_service.get_user_by_id(UUID(token_data.user_id))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "id": str(user.id),
        "username": user.username,
        "display_name": user.display_name,
        "email": user.email,
        "bio": user.bio,
        "avatar_url": user.avatar_url,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }
