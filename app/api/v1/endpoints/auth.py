"""
API эндпоинты для аутентификации - исправленная версия для продакшена
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.services.auth import AuthService
from app.schemas.user import UserCreate, UserLogin, AuthResponse, TokenResponse, User

router = APIRouter()
security = HTTPBearer()


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Получение сервиса аутентификации"""
    return AuthService(db)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """Получение текущего пользователя из токена"""
    token = credentials.credentials
    payload = auth_service.verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = auth_service.get_user_by_id(int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


@router.post("/login", response_model=AuthResponse)
async def login(
    login_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Вход пользователя"""
    user = auth_service.authenticate_user(login_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Создаем access токен
    access_token = auth_service.create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    # Создаем refresh токен
    refresh_token = auth_service.create_refresh_token(user.id)
    
    # Возвращаем оба токена в ответе (без cookies)
    return AuthResponse(
        token=access_token, 
        user=user,
        refresh_token=refresh_token  # Добавляем refresh_token в ответ
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: dict,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Обновление access токена"""
    # Получаем refresh токен из тела запроса
    refresh_token = refresh_data.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh токен не найден"
        )
    
    # Проверяем refresh токен
    user = auth_service.verify_refresh_token(refresh_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или истекший refresh токен"
        )
    
    # Создаем новый access токен
    access_token = auth_service.create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    # Создаем новый refresh токен
    new_refresh_token = auth_service.create_refresh_token(user.id)
    
    # Возвращаем оба токена в ответе (без cookies)
    return TokenResponse(
        token=access_token,
        refresh_token=new_refresh_token  # Добавляем refresh_token в ответ
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Выход пользователя"""
    # Отзываем все refresh токены пользователя
    auth_service.revoke_all_user_tokens(current_user.id)
    
    # Возвращаем успешный статус (cookies больше не используются)


@router.get("/profile", response_model=User)
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    """Получение профиля текущего пользователя"""
    return current_user


@router.get("/health")
async def health_check():
    """Проверка состояния модуля аутентификации"""
    return {"status": "ok", "module": "auth"}
