"""
Настройка базы данных
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.config import settings

# Создаем движок базы данных
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()


def get_db():
    """Получение сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def init_db():
    """Инициализация базы данных"""
    # Импортируем все модели для создания таблиц
    from app.models.user import User
    from app.models.car import Car
    from app.models.refresh_token import RefreshToken
    from app.models.additional_service import AdditionalService
    
    # Создаем все таблицы
    Base.metadata.create_all(bind=engine)
