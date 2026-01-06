# Linap2 - PlantUML Диаграммы Прецедентов

Этот документ описывает все диаграммы системы Linap2, созданные в формате PlantUML.

## 📋 Список диаграмм

### 1. **usecase_diagram.puml** - Диаграмма прецедентов (Use Cases)
**Описание:** Показывает все прецеденты (use cases) системы и взаимодействие пользователя с приложением.

**Актеры:**
- Пользователь (User)
- Система (System)

**Основные группы прецедентов:**

#### Аутентификация (UC1-UC4)
- UC1: Регистрация
- UC2: Вход в систему
- UC3: Выход из системы
- UC4: Восстановление пароля

#### Управление профилем (UC5-UC8)
- UC5: Просмотр профиля
- UC6: Изменить ник
- UC7: Загрузить аватар
- UC8: Изменить пароль

#### Управление видео (UC9-UC12)
- UC9: Загрузить видео
- UC10: Просмотреть видео
- UC11: Удалить видео
- UC12: Отредактировать видео

#### Взаимодействие с видео (UC13-UC16)
- UC13: Лайкнуть видео
- UC14: Дислайкнуть видео
- UC15: Добавить комментарий
- UC16: Удалить комментарий

#### Поиск и фильтрация (UC17-UC18)
- UC17: Фильтровать видео
- UC18: Поиск видео

#### Системные операции (UC19-UC22)
- UC19: Получить уведомление
- UC20: Сохранить видео файл
- UC21: Обновить статистику
- UC22: Верифицировать токен

**Типы связей:**
- `-->` Прямое взаимодействие пользователя
- `<<include>>` Обязательный прецедент (используется всегда)
- `<<extend>>` Опциональный прецедент (может использоваться)
- `..>` Расширение функциональности

---

### 2. **sequence_video_upload.puml** - Диаграмма последовательности загрузки видео
**Описание:** Подробный процесс загрузки видео от пользователя до сохранения в БД.

**Участники:**
1. Пользователь (Frontend)
2. Frontend JavaScript
3. Backend FastAPI
4. Файловая система
5. PostgreSQL БД

**Основной процесс:**
```
1. Пользователь нажимает "Загрузить видео"
   ↓
2. Открывается форма загрузки (modalWindow)
   ↓
3. Пользователь заполняет форму:
   - title (название)
   - description (описание)
   - agent (персонаж)
   - side (сторона: Attack/Defense)
   - file (видеофайл)
   ↓
4. Frontend валидирует данные
   ↓
5. Frontend создает FormData с файлом
   ↓
6. Отправляет POST /videos/upload
   ↓
7. Backend:
   - Декодирует JWT токен
   - Валидирует параметры
   - Проверяет расширение файла
   ↓
8. Сохранение файла:
   - Генерирует уникальное имя
   - Создает директорию uploads/videos/
   - Асинхронно сохраняет (aiofiles)
   ↓
9. Создание записи в БД:
   - INSERT INTO videos
   ↓
10. Backend возвращает успех + video_url
    ↓
11. Frontend обновляет профиль
    ↓
12. Пользователь видит загруженное видео
```

**Валидация файла:** MP4, MOV, octet-stream

**Прогресс загрузки:** XHR progress event listener

---

### 3. **sequence_video_playback.puml** - Диаграмма последовательности просмотра видео
**Описание:** Процесс загрузки видео со страницы, открытия плеера и взаимодействия (лайки, дислайки).

**Основной процесс:**

#### Загрузка видео
```
1. Пользователь открывает страницу
   ↓
2. Frontend запрашивает GET /videos
   ↓
3. Backend получает список видео из БД
   ↓
4. Frontend рендерит видео карточки
   ↓
5. Отображаются карточки с thumbnail, title, описанием
```

#### Клик по видео
```
1. Пользователь кликает на карточку видео
   ↓
2. Frontend вызывает openVideoPlayer(video)
   ↓
3. Заполняет HTML5 video element
   ↓
4. Показывает modal окно
   ↓
5. Автоматически запускает воспроизведение
```

#### Лайк/Дислайк
```
1. Пользователь кликает "👍 Нравится"
   ↓
2. Frontend отправляет POST /videos/{id}/like
   ↓
3. Backend проверяет JWT
   ↓
4. Если уже лайкил → удаляет лайк
   Если нет → добавляет лайк
   ↓
5. UPDATE videos SET likes = likes + 1
   ↓
6. Frontend обновляет счетчик
```

#### Закрытие плеера
```
1. Пользователь нажимает кнопку '✕'
   ↓
2. Frontend паузирует видео
   ↓
3. Скрывает modal окно
```

---

### 4. **architecture_diagram.puml** - Диаграмма архитектуры системы
**Описание:** Общая архитектура приложения и взаимодействие компонентов.

**Слои архитектуры:**

#### 1. Client Layer (Фронтенд)
- HTML5/CSS3 - структура и стили
- JavaScript (Vanilla JS) - логика приложения
- Fetch API + XMLHttpRequest - сетевые запросы

#### 2. Network Layer
- HTTP/HTTPS протокол

#### 3. Server Layer (Бэкенд)
**FastAPI Application:**
- **Router Layer** - маршрутизация запросов
  - `/auth` - аутентификация
  - `/users` - управление пользователями
  - `/videos` - видео операции
  - `/comments` - комментарии
  - `/tags` - теги
  
- **Service Layer** - бизнес-логика
  - Валидация данных
  - CRUD операции
  - Управление правами доступа
  - Статистика
  
- **Model Layer** - ORM модели (SQLAlchemy)
  - User, AuthAccount
  - Video, VideoTag
  - Comment, Like, Dislike
  - Tag, Agent, Ability, Post, Map
  
- **Schema Layer** - Pydantic валидация
  - Сериализация/десериализация JSON
  
- **JWT Authentication** - проверка токенов
- **File Storage** - хранение файлов (uploads/)

#### 4. Data Layer
- **PostgreSQL Database** - основное хранилище
- **Alembic Migrations** - версионирование схемы БД

#### 5. External Services
- **File System** - сохранение файлов на диск

---

### 5. **datamodel_diagram.puml** - Диаграмма моделей данных (ERD)
**Описание:** Структура таблиц БД и связи между ними.

**Основные сущности:**

#### User (Пользователь)
```
- id: UUID (PK)
- username: String (UNIQUE)
- email: String (UNIQUE)
- hashed_password: String
- display_name: String
- avatar_url: String
- is_active: Boolean = True
- created_at, updated_at: DateTime
```

#### Video (Видео)
```
- id: UUID (PK)
- owner_id: UUID (FK → User)
- title: String
- description: String
- video_url: String
- thumbnail_url: String
- agent_id: UUID (FK → Agent, NULLABLE)
- side: String (Attack/Defense)
- views: Integer = 0
- likes: Integer = 0
- dislikes: Integer = 0
- created_at, updated_at: DateTime
```

#### Comment (Комментарий)
```
- id: UUID (PK)
- video_id: UUID (FK → Video)
- author_id: UUID (FK → User)
- content: String
- created_at, updated_at: DateTime
```

#### Like / Dislike
```
- id: UUID (PK)
- video_id: UUID (FK → Video)
- user_id: UUID (FK → User)
- created_at: DateTime
- UNIQUE constraint: (video_id, user_id)
```

#### Tag (Тег)
```
- id: UUID (PK)
- name: String (UNIQUE)
- created_at: DateTime
```

#### VideoTag (Связь Видео-Тег)
```
- id: UUID (PK)
- video_id: UUID (FK)
- tag_id: UUID (FK)
- UNIQUE constraint: (video_id, tag_id)
```

#### Agent (Персонаж)
```
- id: UUID (PK)
- name: String (UNIQUE)
- description: String
- created_at: DateTime
```

#### Ability (Умение персонажа)
```
- id: UUID (PK)
- agent_id: UUID (FK → Agent)
- name: String
- description: String
- created_at: DateTime
```

#### Дополнительные сущности
- **AuthAccount** - социальная аутентификация
- **Session** - активные сессии пользователя
- **EmailVerification** - верификация почты
- **PasswordReset** - восстановление пароля
- **Post** - посты пользователей
- **PostTag** - теги для постов
- **Map** - карты CS2

**Связи (Relations):**
- User 1:* Video (владельца видео)
- User 1:* Comment (автор комментариев)
- User 1:* Like/Dislike (создатель лайков)
- Video 1:* Comment (получает комментарии)
- Video 1:* Like/Dislike (получает оценки)
- Video *:1 Agent (использует персонажа)
- Agent 1:* Ability (имеет умения)
- Tag 1:* VideoTag (применяется к видео)

---

### 6. **sequence_authentication.puml** - Диаграмма последовательности аутентификации
**Описание:** Полный цикл аутентификации от регистрации до выхода.

**Процессы:**

#### 1. Регистрация (Register)
```
1. Пользователь заполняет форму
   - username
   - email
   - password (мин. 8 символов)
   - displayName
   ↓
2. Frontend валидирует локально
   ↓
3. POST /auth/register
   ↓
4. Backend проверяет уникальность username и email
   ↓
5. Хеширует пароль (bcrypt)
   ↓
6. INSERT INTO users
   ↓
7. Создает токен верификации email
   ↓
8. Frontend показывает успех
   "На ваш email отправлена ссылка"
```

#### 2. Вход (Login)
```
1. Пользователь заполняет форму
   - username (или email)
   - password
   ↓
2. POST /auth/login
   ↓
3. Backend ищет пользователя в БД
   ↓
4. Проверяет пароль (bcrypt.verify())
   ↓
5. Генерирует JWT токен:
   - algorithm: HS256
   - payload: {user_id, username, exp}
   - key: SECRET_KEY
   ↓
6. Сохраняет сессию в БД
   ↓
7. Возвращает access_token
   ↓
8. Frontend:
   - Сохраняет токен в localStorage
   - GET /users/me для получения профиля
   - Обновляет UI
```

#### 3. Защищенные запросы
```
Каждый запрос требующий аутентификации:

1. Frontend добавляет заголовок:
   Authorization: Bearer <TOKEN>
   ↓
2. Backend функция get_current_user():
   - Извлекает токен из заголовка
   - Проверяет "Bearer " префикс
   - Декодирует JWT
   - Проверяет подпись (SECRET_KEY)
   - Проверяет время жизни (exp)
   - Возвращает TokenData(user_id, username)
   ↓
3. Если токен невалидный:
   - Возвращает 401 Unauthorized
   - Frontend удаляет токен
   - Показывает форму входа
   ↓
4. Если токен валидный:
   - Выполняет основную операцию
   - Использует user_id для проверки прав
```

#### 4. Выход (Logout)
```
1. Пользователь нажимает "Выход"
   ↓
2. Frontend:
   - Удаляет токен (localStorage.removeItem)
   - Очищает currentUser
   - Показывает форму входа
   ↓
3. Backend:
   - DELETE FROM sessions WHERE user_id = X
```

**Безопасность:**
- ✅ Пароли хешируются bcrypt
- ✅ JWT подписи проверяются
- ✅ Токены с ограниченным временем жизни
- ✅ Токены хранятся в localStorage
- ✅ HTTPS рекомендуется для production
- ✅ Возможна опция HttpOnly cookies

---

## 🔧 Как использовать диаграммы

### Просмотр диаграмм онлайн
Используйте один из этих сервисов:

1. **PlantUML Online Editor**
   - http://www.plantuml.com/plantuml/uml
   - Копируйте содержимое .puml файла
   - Нажмите "Render"

2. **Plant UML Server**
   - http://www.plantuml.com/plantuml/svg
   - Используйте через REST API

3. **VS Code Extension**
   - Установите "PlantUML" extension
   - Откройте .puml файл
   - Нажмите `Alt+D` для предпросмотра

### Экспорт диаграмм
```bash
# Требует установку PlantUML и Graphviz

# Экспорт в PNG
plantuml -tpng usecase_diagram.puml

# Экспорт в SVG
plantuml -tsvg usecase_diagram.puml

# Экспорт в PDF
plantuml -tpdf usecase_diagram.puml
```

### Интеграция в документацию
Для добавления в markdown файлы:

```markdown
![Use Case Diagram](docs/usecase_diagram.puml)

Или встроить через PlantUML сервер:
![Use Cases](http://www.plantuml.com/plantuml/svg/...)
```

---

## 📚 Связь между диаграммами

```
┌─────────────────────────────────────┐
│   usecase_diagram.puml              │
│   (Что может делать пользователь)   │
└──────────────┬──────────────────────┘
               │ детализирует
               ├──────────────────────────┐
               │                          │
    ┌──────────▼─────────┐     ┌──────────▼──────────────┐
    │ sequence_auth.puml │     │ sequence_upload.puml    │
    │ (Как логин работает)      (Как загрузка работает)  │
    └──────────┬─────────┘     └──────────┬──────────────┘
               │                          │
               └──────────────┬───────────┘
                              │
                   ┌──────────▼────────────┐
                   │ architecture.puml     │
                   │ (Архитектура системы) │
                   └──────────┬────────────┘
                              │ использует
                   ┌──────────▼────────────┐
                   │ datamodel.puml        │
                   │ (Структура БД)        │
                   └───────────────────────┘
```

---

## 📝 Примечания

- Все диаграммы соответствуют текущему состоянию проекта
- Используется PlantUML синтаксис версии 1.2024+
- Диаграммы можно обновлять при добавлении новых features
- Рекомендуется хранить диаграммы в git вместе с кодом

---

**Создано:** December 17, 2025  
**Для проекта:** Linap2 - CS2 Video Platform  
**Формат:** PlantUML (.puml)
