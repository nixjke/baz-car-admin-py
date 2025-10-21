"""
FastAPI приложение для управления автомобилями
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import init_db
from app.api.v1.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Инициализация базы данных при запуске
    await init_db()
    yield
    # Очистка ресурсов при завершении
    pass


# Создание FastAPI приложения
app = FastAPI(
    title="Baz Car Admin API",
    description="API для управления автомобилями",
    version="1.0.0",
    lifespan=lifespan
)

# Статические файлы для документации
if os.path.exists("docs"):
    app.mount("/docs", StaticFiles(directory="docs"), name="docs")

# Статические файлы для загрузок
if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Настройка CORS
# Добавляем домен baz-car-server.online программно
cors_origins = settings.ALLOWED_HOSTS.copy()
if "http://baz-car-server.online" not in cors_origins:
    cors_origins.extend([
        "http://baz-car-server.online",
        "https://baz-car-server.online"
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение API роутеров
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Главная страница с информацией об API"""
    return {
        "message": "Baz Car Admin API",
        "version": "1.0.0",
        "endpoints": {
            "auth": {
                "register": "POST /api/v1/auth/register",
                "login": "POST /api/v1/auth/login",
                "refresh": "POST /api/v1/auth/refresh",
                "profile": "GET /api/v1/auth/profile",
                "logout": "POST /api/v1/auth/logout"
            },
            "health": "GET /api/v1/health",
            "cars": {
                "list": "GET /api/v1/cars",
                "get": "GET /api/v1/cars/{id}",
                "create": "POST /api/v1/cars",
                "update": "PUT/PATCH /api/v1/cars/{id}",
                "delete": "DELETE /api/v1/cars/{id}",
                "upload_images": "POST /api/v1/cars/{id}/images",
                "upload_temp": "POST /api/v1/cars/uploads/temp",
                "cleanup_uploads": "POST /api/v1/cars/uploads/cleanup"
            }
        }
    }


@app.get("/health")
async def health_check():
    """Проверка состояния сервиса"""
    return {"status": "ok", "module": "baz-car-admin"}


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
