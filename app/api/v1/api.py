"""
Основной роутер API v1
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, cars, additional_services

api_router = APIRouter()

# Подключаем роутеры
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(cars.router, prefix="/cars", tags=["cars"])
api_router.include_router(additional_services.router, prefix="/additional-services", tags=["additional-services"])
