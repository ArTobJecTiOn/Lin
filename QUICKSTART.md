# 🚀 Быстрый старт Linap2 Backend

## 1️⃣ Установка зависимостей

```bash
# Убедитесь, что установлены Python 3.10+ и poetry
python --version  # Должно быть >= 3.10
poetry --version

# Установить зависимости
cd Linap2
poetry install
```

## 2️⃣ Настройка базы данных

### Вариант A: PostgreSQL (рекомендуется)

```bash
# 1. Установить PostgreSQL
# Windows: https://www.postgresql.org/download/windows/
# Mac: brew install postgresql
# Linux: sudo apt-get install postgresql

# 2. Создать .env файл в корне проекта
cat > .env << EOF
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=linap2
API_BASE_PORT=8000
EOF

# 3. Инициализировать БД (создать таблицы)
poetry run alembic upgrade head
```

### Вариант B: SQLite (для разработки)

```bash
# Отредактируйте app/core/settings/settings.py
# Раскомментируйте SQLite конфиг или создайте новый
```

## 3️⃣ Запуск сервера

```bash
# Запуск в режиме разработки с auto-reload
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Или просто
poetry run uvicorn app.main:app --reload
```

## 4️⃣ Проверка работы

Откройте в браузере:
- **API docs**: http://localhost:8000/docs
- **Health check**: http://localhost:8000/health
- **ReDoc**: http://localhost:8000/redoc

## ✅ Первые шаги

### 1. Регистрация (в Swagger UI или через curl)

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'

# Ответ содержит access_token
```

### 2. Копируем токен и используем в запросах

```bash
# Замените на ваш токен
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."

# Получить информацию о себе
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/users/me
```

### 3. Создаем пост

```bash
curl -X POST http://localhost:8000/api/v1/posts/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "owner_id": "your-user-uuid",
    "title": "My First Post",
    "slug": "my-first-post",
    "content": "Post content here"
  }'
```

## 📊 Структура проекта

```
Linap2/
├── .env                 # Переменные окружения (не коммитить!)
├── .gitignore
├── README.md           # Основная документация
├── FRONTEND_GUIDE.md   # Руководство для фронтенда
├── QUICKSTART.md       # Этот файл
├── api_examples.sh     # Примеры API запросов
├── tests_api.py        # Тесты API
├── pyproject.toml      # Зависимости проекта
├── alembic/            # Миграции БД
│   └── versions/       # Файлы миграций
├── app/
│   ├── main.py         # Entry point
│   ├── core/
│   │   ├── security.py # JWT и хэширование
│   │   ├── database/
│   │   └── settings/
│   ├── models/         # SQLAlchemy модели
│   ├── service/        # Бизнес-логика
│   ├── routing/        # API роутеры
│   └── schemas/        # Pydantic валидация
```

## 🔒 Безопасность в production

### Перед развертыванием:

```python
# app/core/security.py - изменить SECRET_KEY
SECRET_KEY = "your-super-secret-key-change-this"  # ❌ Плохо
SECRET_KEY = os.getenv("SECRET_KEY", "default")   # ✅ Хорошо

# Установить в .env
SECRET_KEY=your-super-secure-random-string
```

### Окружение production

```bash
# Установить переменные окружения
export POSTGRES_HOST=prod-database.example.com
export POSTGRES_PASSWORD=secure_password
export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')

# Запустить с Gunicorn
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

## 🐛 Решение проблем

### Проблема: "ModuleNotFoundError: No module named 'app'"

**Решение:**
```bash
# Убедитесь, что вы в корне проекта Linap2
ls app/  # Должны быть папки: core, models, service, routing, schemas

# Переустановите зависимости
poetry install

# Запустите снова
poetry run uvicorn app.main:app --reload
```

### Проблема: "Connection refused" при подключении к БД

**Решение:**
```bash
# Проверьте .env файл
cat .env

# Проверьте что PostgreSQL запущен
# Windows: Services -> PostgreSQL
# Mac: brew services list
# Linux: sudo systemctl status postgresql

# Создайте БД вручную (если нужно)
createdb linap2 -U postgres
```

### Проблема: "SQLALCHEMY_DATABASE_URL is not set"

**Решение:**
```bash
# Создайте .env файл
cat > .env << EOF
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=linap2
API_BASE_PORT=8000
EOF
```

## 📚 Дополнительные ресурсы

- [FastAPI документация](https://fastapi.tiangolo.com/)
- [SQLAlchemy async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [JWT токены](https://en.wikipedia.org/wiki/JSON_Web_Token)
- [Alembic миграции](https://alembic.sqlalchemy.org/)

## 🤝 Подключение фронтенда

Frontend может подключаться к:
```
http://localhost:8000/api/v1

Примеры:
- http://localhost:8000/api/v1/posts/
- http://localhost:8000/api/v1/users/me
- http://localhost:8000/api/v1/auth/login
```

Смотрите [FRONTEND_GUIDE.md](FRONTEND_GUIDE.md) для примеров JavaScript/React/Vue

## 🎯 Next Steps

1. ✅ Backend запущен
2. 🔄 Подключить фронтенд
3. 📝 Добавить больше функциональности
4. 🧪 Написать тесты
5. 🚀 Развернуть на сервере

## ✉️ Поддержка

Если возникли проблемы, проверьте:
- Версию Python (должна быть >= 3.10)
- Установлены ли все зависимости (`poetry install`)
- Запущена ли база данных
- Правильны ли переменные в .env

---

**Готово к разработке! 🚀**
