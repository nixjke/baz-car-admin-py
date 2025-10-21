"""
Схемы для пользователей
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator  # pyright: ignore[reportMissingImports]


class UserCreate(BaseModel):
    """Схема для создания пользователя (только username и пароль)"""
    username: str
    password: str

    @field_validator('password')
    @classmethod
    def truncate_password(cls, v: str) -> str:
        """Обрезаем пароль до 72 байт для bcrypt"""
        if isinstance(v, str):
            return v.encode('utf-8')[:72].decode('utf-8', errors='ignore')
        return v


class UserLogin(BaseModel):
    """Схема для входа пользователя"""
    username: str
    password: str

    @field_validator('password')
    @classmethod
    def truncate_password(cls, v: str) -> str:
        """Обрезаем пароль до 72 байт для bcrypt"""
        if isinstance(v, str):
            return v.encode('utf-8')[:72].decode('utf-8', errors='ignore')
        return v


class User(BaseModel):
    """Схема пользователя для ответа"""
    id: int
    username: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Схема ответа при аутентификации"""
    token: str
    user: User
    refresh_token: str


class TokenResponse(BaseModel):
    """Схема ответа с токеном"""
    token: str
    refresh_token: str
