"""
Схемы для автомобилей
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class CarBase(BaseModel):
    """Базовая схема автомобиля"""
    name: str
    category: Optional[str] = None
    category_ru: Optional[str] = None
    price: Optional[int] = None
    price_3plus_days: Optional[int] = None
    description: Optional[str] = None
    description_ru: Optional[str] = None
    features: Optional[List[str]] = None
    features_ru: Optional[List[str]] = None
    specifications: Optional[Dict[str, Any]] = None
    available: bool = True
    rating: float = 0.0
    fuel_type: Optional[str] = None
    restrictions: Optional[Dict[str, Any]] = None
    additional_services: Optional[List[int]] = None


class CarCreate(CarBase):
    """Схема для создания автомобиля"""
    images: Optional[List[str]] = None


class CarUpdate(BaseModel):
    """Схема для обновления автомобиля"""
    name: Optional[str] = None
    category: Optional[str] = None
    category_ru: Optional[str] = None
    price: Optional[int] = None
    price_3plus_days: Optional[int] = None
    images: Optional[List[str]] = None
    description: Optional[str] = None
    description_ru: Optional[str] = None
    features: Optional[List[str]] = None
    features_ru: Optional[List[str]] = None
    specifications: Optional[Dict[str, Any]] = None
    available: Optional[bool] = None
    rating: Optional[float] = None
    fuel_type: Optional[str] = None
    restrictions: Optional[Dict[str, Any]] = None
    additional_services: Optional[List[int]] = None


class Car(CarBase):
    """Схема автомобиля для ответа"""
    id: int
    images: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UploadResponse(BaseModel):
    """Схема ответа при загрузке файлов"""
    uploaded: List[str]


class CleanupResponse(BaseModel):
    """Схема ответа при очистке файлов"""
    deleted: int
