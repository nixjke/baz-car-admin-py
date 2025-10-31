"""
Конфигурация приложения - исправленная версия для продакшена
"""
import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Основные настройки
    PROJECT_NAME: str = "Baz Car Admin API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # База данных
    DATABASE_URL: str = "sqlite:///./baz_car.db"
    
    # JWT настройки
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # CORS настройки - исправлено для продакшена
    ALLOWED_HOSTS: List[str] = [
        "http://baz-car-server.online",  # Домен сервера (ПРИОРИТЕТ)
        "https://baz-car-server.online",  # HTTPS версия сервера
        "http://www.baz-car.fun",  # Ваш домен админки
        "https://www.baz-car.fun",  # HTTPS версия
        "http://baz-car.fun",  # Без www
        "https://baz-car.fun",  # HTTPS без www
        "http://localhost:5173",  # Админка
        "http://localhost:5174",  # Основной фронт
        "http://localhost:3000", 
        "http://127.0.0.1:5173", 
        "http://127.0.0.1:5174",  # Основной фронт
        "http://127.0.0.1:3000",
        "http://91.229.8.235:5173",  # IP сервера
        "http://91.229.8.235:3000",
    ]
    
    # Файловое хранилище
    UPLOAD_DIR: str = "uploads"
    TEMP_UPLOAD_DIR: str = "uploads/temp"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    # Порт сервера
    PORT: int = 8080
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Игнорировать дополнительные поля


# Создаем экземпляр настроек
settings = Settings()
