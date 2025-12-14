from typing import Optional
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.user import User
from app.models.auth_account import AuthAccount
from app.core.security import get_password_hash, verify_password, create_access_token
from datetime import timedelta


class AuthService:
    """Сервис для аутентификации"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def register(
        self,
        username: str,
        email: str,
        password: str,
        display_name: Optional[str] = None
    ) -> User:
        """Регистрация нового пользователя"""
        print(f"[REGISTER] Attempting to register user: {username}, email: {email}")
        
        # Проверяем уникальность username
        existing_user = await self.session.execute(
            select(User).where(User.username == username)
        )
        if existing_user.scalars().first():
            print(f"[REGISTER] Username already exists: {username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

        # Проверяем уникальность email
        existing_email = await self.session.execute(
            select(User).where(User.email == email)
        )
        if existing_email.scalars().first():
            print(f"[REGISTER] Email already registered: {email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Создаем пользователя
        user = User(
            username=username,
            email=email,
            display_name=display_name or username,
            is_active=True
        )

        self.session.add(user)
        await self.session.flush()
        
        print(f"[REGISTER] User created with ID: {user.id}")

        # Создаем учетную запись с паролем
        password_hash = get_password_hash(password)
        print(f"[REGISTER] Password hashed, creating auth account...")
        
        auth_account = AuthAccount(
            user_id=user.id,
            provider="local",
            password_hash=password_hash,
            is_primary=True
        )

        self.session.add(auth_account)
        await self.session.commit()
        await self.session.refresh(user)

        print(f"[REGISTER] Registration successful for user: {username}")
        return user

    async def authenticate(self, username: str, password: str) -> User:
        """Аутентифицировать пользователя"""
        print(f"[AUTH] Attempting to authenticate user: {username}")
        
        # Находим пользователя
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        user = result.scalars().first()

        if not user:
            print(f"[AUTH] User not found: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        print(f"[AUTH] User found: {user.username}, is_active: {user.is_active}")

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated"
            )

        # Находим учетную запись с паролем
        auth_result = await self.session.execute(
            select(AuthAccount).where(
                AuthAccount.user_id == user.id,
                AuthAccount.provider == "local"
            )
        )
        auth_account = auth_result.scalars().first()

        if not auth_account or not auth_account.password_hash:
            print(f"[AUTH] No auth account found for user: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        print(f"[AUTH] Auth account found, verifying password...")
        
        # Проверяем пароль
        password_valid = verify_password(password, auth_account.password_hash)
        print(f"[AUTH] Password verification result: {password_valid}")
        
        if not password_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        print(f"[AUTH] Authentication successful for user: {username}")
        return user

    async def change_password(
        self,
        user_id: uuid.UUID,
        old_password: str,
        new_password: str
    ) -> bool:
        """Изменить пароль пользователя"""
        # Находим пользователя
        user = await self.session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Находим учетную запись
        result = await self.session.execute(
            select(AuthAccount).where(
                AuthAccount.user_id == user_id,
                AuthAccount.provider == "local"
            )
        )
        auth_account = result.scalars().first()

        if not auth_account or not auth_account.password_hash:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User has no local password"
            )

        # Проверяем старый пароль
        if not verify_password(old_password, auth_account.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Old password is incorrect"
            )

        # Устанавливаем новый пароль
        auth_account.password_hash = get_password_hash(new_password)
        await self.session.commit()

        return True

    def create_access_token(self, user_id: uuid.UUID, username: str) -> str:
        """Создать JWT токен"""
        token_data = {
            "user_id": str(user_id),
            "username": username
        }
        return create_access_token(token_data, expires_delta=timedelta(hours=24))
