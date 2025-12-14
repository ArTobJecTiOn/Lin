"""
Тестовые примеры для проверки API
Запуск: pytest tests_api.py -v
"""

import pytest
import json
from httpx import AsyncClient


# Тестовые данные
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123",
    "display_name": "Test User"
}

TEST_POST = {
    "title": "Test Post",
    "slug": "test-post",
    "content": "This is test content",
    "excerpt": "Test excerpt"
}


@pytest.mark.asyncio
async def test_health_check():
    """Проверка статуса API"""
    from app.main import app
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_user_registration():
    """Тест регистрации пользователя"""
    from app.main import app
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/register",
            json=TEST_USER
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["token_type"] == "bearer"
        assert data["username"] == TEST_USER["username"]
        assert "access_token" in data
        assert "user_id" in data


@pytest.mark.asyncio
async def test_user_login():
    """Тест входа в систему"""
    from app.main import app
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Сначала регистрируемся
        await client.post("/api/v1/auth/register", json=TEST_USER)
        
        # Затем логинимся
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": TEST_USER["username"],
                "password": TEST_USER["password"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["username"] == TEST_USER["username"]


@pytest.mark.asyncio
async def test_invalid_login():
    """Тест входа с неверным паролем"""
    from app.main import app
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Регистрируемся
        await client.post("/api/v1/auth/register", json=TEST_USER)
        
        # Пытаемся логиниться с неверным паролем
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": TEST_USER["username"],
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]


@pytest.mark.asyncio
async def test_duplicate_username():
    """Тест на попытку регистрации с существующим username"""
    from app.main import app
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Регистрируемся первый раз
        await client.post("/api/v1/auth/register", json=TEST_USER)
        
        # Пытаемся зарегистрироваться с тем же username
        response = await client.post(
            "/api/v1/auth/register",
            json={
                **TEST_USER,
                "email": "different@example.com"
            }
        )
        
        assert response.status_code == 400
        assert "Username already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_post():
    """Тест создания поста"""
    from app.main import app
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Регистрируемся
        reg_response = await client.post("/api/v1/auth/register", json=TEST_USER)
        user_id = reg_response.json()["user_id"]
        token = reg_response.json()["access_token"]
        
        # Создаем пост
        response = await client.post(
            "/api/v1/posts/",
            json={**TEST_POST, "owner_id": user_id},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["post"]["title"] == TEST_POST["title"]
        assert data["post"]["slug"] == TEST_POST["slug"]


@pytest.mark.asyncio
async def test_get_post():
    """Тест получения поста"""
    from app.main import app
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Регистрируемся
        reg_response = await client.post("/api/v1/auth/register", json=TEST_USER)
        user_id = reg_response.json()["user_id"]
        token = reg_response.json()["access_token"]
        
        # Создаем пост
        create_response = await client.post(
            "/api/v1/posts/",
            json={**TEST_POST, "owner_id": user_id},
            headers={"Authorization": f"Bearer {token}"}
        )
        post_id = create_response.json()["post"]["id"]
        
        # Получаем пост
        response = await client.get(
            f"/api/v1/posts/{post_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert response.json()["title"] == TEST_POST["title"]


@pytest.mark.asyncio
async def test_unauthorized_access():
    """Тест доступа без токена"""
    from app.main import app
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/users/me")
        
        assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
