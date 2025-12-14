from fastapi import APIRouter
from app.routing.auth.auth_router import router as auth_router
from app.routing.users.user_router import router as user_router
from app.routing.posts.post_router import router as post_router
from app.routing.videos.video_router import router as video_router
from app.routing.tags.tag_router import router as tag_router
from app.routing.likes.like_router import router as like_router
from app.routing.comments.comment_router import router as comment_router

# Создаем главный роутер с префиксом /api/v1
api_router = APIRouter(prefix="/api/v1")

# Включаем все роутеры
api_router.include_router(auth_router)
api_router.include_router(user_router, tags=["Users"])
api_router.include_router(post_router, tags=["Posts"])
api_router.include_router(video_router, tags=["Videos"])
api_router.include_router(tag_router, tags=["Tags"])
api_router.include_router(like_router, tags=["Likes"])
api_router.include_router(comment_router, tags=["Comments"])
