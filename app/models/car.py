"""
Модели автомобилей
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Text
from sqlalchemy.dialects.sqlite import JSON

from app.core.database import Base


class Car(Base):
    """Модель автомобиля"""
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String)
    category_ru = Column(String)
    price = Column(Integer)
    price_3plus_days = Column(Integer)
    images = Column(JSON)  # Список путей к изображениям
    description = Column(Text)
    description_ru = Column(Text)
    features = Column(JSON)  # Список особенностей
    features_ru = Column(JSON)  # Список особенностей на русском
    specifications = Column(JSON)  # Технические характеристики
    available = Column(Boolean, default=True)
    rating = Column(Float, default=0.0)
    fuel_type = Column(String)
    restrictions = Column(JSON)  # Ограничения
    additional_services = Column(JSON)  # Список ID дополнительных услуг
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
