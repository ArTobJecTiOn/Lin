import uvicorn
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.database.database import engine
from app.core.settings.settings import settings
from app.models.base import Base
from app.routing.api_router import api_router


# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title="Linap2",
    description="API проекта Linap2",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint (before API router to avoid conflicts)
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Include API router
app.include_router(api_router)

# Mount static files (CSS, JS)
FRONT_DIR = Path(__file__).parent.parent / "front"
app.mount("/static", StaticFiles(directory=str(FRONT_DIR)), name="static")

# Mount uploads directory
UPLOADS_DIR = Path(__file__).parent.parent / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

# Serve index.html at root (must be last to not override other routes)
@app.get("/")
async def serve_frontend():
    index_file = FRONT_DIR / "index.html"
    return FileResponse(index_file)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.API_BASE_PORT,
        reload=True,
    )