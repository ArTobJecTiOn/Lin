# Linap2 - VALORANT Strategies Platform

## 🎮 О проекте

**Linap2** - платформа для публикации и просмотра стратегий VALORANT. Включает полнофункциональный FastAPI backend и фронтенд на Vanilla JS.

## 🚀 Быстрый старт

```bash
# 1. Установить зависимости
poetry install

# 2. Настроить .env (см. раздел "Настройка")
# 3. Инициализировать БД
poetry run alembic upgrade head

# 4. Запустить сервер
poetry run uvicorn app.main:app --reload
```

**Готово!** Откройте http://localhost:8000

## 📋 Что реализовано

### ✅ Backend (FastAPI):
- 🔐 JWT аутентификация (register, login, password change)
- 👤 User management (CRUD, avatar, activate/deactivate)
- 📝 Posts (CRUD, publish/unpublish, views tracking)
- 🎬 Videos (CRUD, likes/dislikes, views, filter by agent/map)
- 🏷️ Tags (CRUD, slug generation)
- ❤️ Likes (like/unlike posts)
- 💬 Comments (CRUD, nested comments)
- 🔄 Полный async/await
- ✅ Pydantic валидация всех запросов/ответов
- 📚 Auto-generated API docs (Swagger/ReDoc)

### ✅ Frontend:
- 🎨 Темная тема в стиле VALORANT
- 🔐 Регистрация и вход пользователей
- 🎬 Просмотр видео стратегий
- 🔍 Фильтрация по агентам и стороне (Attack/Defense)
- 👤 Личный кабинет с видео пользователя
- 💾 Автоматическое сохранение JWT токена

## ⚙️ Настройка

## ⚙️ Настройка

### 1. Переменные окружения

Создайте файл `.env` в корне проекта:
```
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=linap2
API_BASE_PORT=8000
SECRET_KEY=your-secret-key-change-in-production
```

### 2. База данных

```bash
# Инициализировать таблицы
poetry run alembic upgrade head
```

### 3. Запуск

```bash
# Режим разработки с auto-reload
poetry run uvicorn app.main:app --reload

# Или через Python
python -m app.main
```

## 🌐 Доступ

- **Фронтенд**: http://localhost:8000/
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📖 Документация

- [FRONTEND_SETUP.md](FRONTEND_SETUP.md) - Подробная инструкция по фронтенду
- [FRONTEND_GUIDE.md](FRONTEND_GUIDE.md) - Руководство для frontend разработчиков
- [QUICKSTART.md](QUICKSTART.md) - Быстрый старт проекта
- [api_examples.sh](api_examples.sh) - Примеры API запросов (curl)
- [tests_api.py](tests_api.py) - Примеры pytest тестов

## 🛠️ Установка и запуск

```bash
# Установить зависимости
poetry install

# Запустить миграции
poetry run alembic upgrade head

# Запустить сервер
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📡 API Endpoints

### Users (`/api/v1/users`)
- `GET /{user_id}` - получить пользователя
- `GET /username/{username}` - по username
- `POST /` - создать пользователя
- `PUT /{user_id}` - обновить профиль
- `PUT /{user_id}/activate` - активировать
- `PUT /{user_id}/deactivate` - деактивировать

### Posts (`/api/v1/posts`)
- `GET /{post_id}` - получить пост
- `GET /slug/{slug}` - по slug
- `GET /user/{user_id}` - посты пользователя
- `GET /` - опубликованные посты
- `POST /` - создать пост
- `PUT /{post_id}` - обновить пост
- `PUT /{post_id}/publish` - опубликовать
- `DELETE /{post_id}` - удалить пост

### Videos (`/api/v1/videos`)
- `GET /{video_id}` - получить видео
- `GET /user/{user_id}` - видео пользователя
- `GET /agent/{agent}` - видео по агенту
- `GET /map/{map_id}` - видео по карте
- `POST /` - создать видео
- `PUT /{video_id}` - обновить видео
- `POST /{video_id}/like` - лайк видео
- `POST /{video_id}/dislike` - дизлайк видео
- `DELETE /{video_id}` - удалить видео

### Tags (`/api/v1/tags`)
- `GET /` - все теги
- `GET /{tag_id}` - получить тег
- `GET /name/{name}` - тег по имени
- `POST /` - создать тег
- `PUT /{tag_id}` - обновить тег
- `DELETE /{tag_id}` - удалить тег

### Likes (`/api/v1/likes`)
- `GET /post/{post_id}` - лайки поста
- `GET /user/{user_id}` - лайки пользователя
- `POST /post/{post_id}` - поставить лайк
- `DELETE /post/{post_id}` - удалить лайк

### Comments (`/api/v1/comments`)
- `GET /{comment_id}` - получить комментарий
- `GET /post/{post_id}` - комментарии поста
- `GET /user/{user_id}` - комментарии пользователя
- `POST /` - создать комментарий
- `PUT /{comment_id}` - обновить комментарий
- `DELETE /{comment_id}` - удалить комментарий

## 🔗 Подключение фронтенда

### Base URL
```
http://localhost:8000/api/v1
```

### Пример запроса (JavaScript/Fetch)
```javascript
// Получить пользователя
fetch('http://localhost:8000/api/v1/users/123e4567-e89b-12d3-a456-426614174000')
  .then(res => res.json())
  .then(data => console.log(data))

// Создать пост
fetch('http://localhost:8000/api/v1/posts/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    owner_id: 'user-uuid',
    title: 'My Post',
    slug: 'my-post',
    content: 'Post content...'
  })
})
```

### Пример запроса (Axios)
```javascript
import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:8000/api/v1'
});

// GET запрос
API.get('/users/123')

// POST запрос
API.post('/posts/', {
  owner_id: 'user-uuid',
  title: 'Post Title',
  slug: 'post-title'
})
```

## 📚 Документация API

Когда сервер запущен:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## ⚙️ Структура проекта

```
app/
├── core/
│   ├── database/
│   │   └── database.py          # Конфиг БД
│   └── settings/
│       └── settings.py          # Настройки приложения
├── models/
│   ├── user.py
│   ├── post.py
│   ├── video.py
│   ├── tag.py
│   ├── like.py
│   ├── comment.py
│   └── ...
├── service/
│   ├── user_service.py          # Бизнес-логика пользователей
│   ├── post_service.py
│   ├── video_service.py
│   └── ...
├── routing/
│   ├── api_router.py            # Главный маршрутизатор
│   ├── users/
│   │   └── user_router.py
│   ├── posts/
│   │   └── post_router.py
│   └── ...
├── schemas/
│   ├── user.py                  # Pydantic модели
│   ├── post.py
│   └── ...
└── main.py                       # Entry point
```

## � Авторизация JWT

### ✅ Реализовано:
- **Регистрация** пользователей с хэшированием паролей (bcrypt)
- **Вход** с username/password
- **JWT токены** - действуют 24 часа
- **Защита** маршрутов с авторизацией

### Регистрация
```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password",
  "display_name": "John Doe"
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "john_doe",
  "expires_in": 86400
}
```

### Вход
```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "secure_password"
}
```

### Использование токена в запросах
```bash
# В заголовке Authorization
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...

# Пример с curl
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/users/me
```

### JavaScript/Fetch
```javascript
// Вход и сохранение токена
const response = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'john_doe',
    password: 'password'
  })
});

const data = await response.json();
localStorage.setItem('token', data.access_token);

// Использовать токен для защищённых запросов
const token = localStorage.getItem('token');
fetch('http://localhost:8000/api/v1/users/me', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

### Axios
```javascript
import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:8000/api/v1'
});

// Добавить интерцептор для токена
API.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Использовать
API.post('/auth/login', { username, password });
API.get('/users/me');
```

---

## ⚠️ Статус исправлений:

✅ **Авторизация JWT** - Полностью реализована
- Регистрация и вход работают
- Пароли хранятся безопасно (bcrypt)
- Токены действуют 24 часа

✅ **Обработка ошибок** - Все эндпоинты валидируют:
```json
{
  "detail": "Invalid credentials",
  "error_code": "AUTH_ERROR"
}
```

✅ **UUID для ID** - Везде используются UUID для безопасности

## 🔮 Рекомендации для дальнейшей разработки

1. ✅ **Authentication** - JWT токены (готово!)
2. **Rate Limiting** - ограничение запросов
3. **Caching** - Redis для кэширования
4. **Email verification** - подтверждение email
5. **File uploads** - загрузка файлов (аватары, видео)
6. **Websockets** - real-time уведомления
7. **Tests** - unit и integration тесты
8. **Logging** - логирование ошибок

## ✅ Ready to go!

Проект готов к подключению фронтенда и дальнейшей разработке!
