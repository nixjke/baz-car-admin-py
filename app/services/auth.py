"""
Сервис аутентификации
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.schemas.user import UserCreate, UserLogin


# Контекст для хеширования паролей
# Настраиваем bcrypt для автоматического обрезания паролей
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__ident="2b",
    bcrypt__default_rounds=12,
)


class AuthService:
    """Сервис аутентификации"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        # Обрезаем пароль до 72 символов для совместимости с bcrypt
        plain_password = plain_password[:72]
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Хеширование пароля"""
        # Обрезаем пароль до 72 символов для совместимости с bcrypt
        password = password[:72]
        return pwd_context.hash(password)
    
    def create_user(self, user_data: UserCreate) -> User:
        """Создание пользователя"""
        # Проверяем, существует ли пользователь с таким username
        existing_user = self.db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise ValueError("Пользователь с таким username уже существует")
        
        # Создаем нового пользователя
        hashed_password = self.get_password_hash(user_data.password)
        db_user = User(
            username=user_data.username,
            password=hashed_password,
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def authenticate_user(self, login_data: UserLogin) -> Optional[User]:
        """Аутентификация пользователя"""
        user = self.db.query(User).filter(User.username == login_data.username).first()
        if not user:
            return None
        if not self.verify_password(login_data.password, user.password):
            return None
        if not user.is_active:
            return None
        return user
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Получение пользователя по ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Получение пользователя по имени пользователя"""
        return self.db.query(User).filter(User.username == username).first()
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Создание access токена"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Проверка токена"""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            return payload
        except JWTError:
            return None
    
    def create_refresh_token(self, user_id: int) -> str:
        """Создание refresh токена"""
        # Удаляем старые refresh токены пользователя
        self.db.query(RefreshToken).filter(RefreshToken.user_id == user_id).delete()
        
        # Создаем новый refresh токен
        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        token_data = {
            "user_id": user_id,
            "exp": expires_at.timestamp()
        }
        token = jwt.encode(token_data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        
        # Сохраняем в базе данных
        db_token = RefreshToken(
            token=token,
            user_id=user_id,
            expires_at=expires_at
        )
        self.db.add(db_token)
        self.db.commit()
        
        return token
    
    def verify_refresh_token(self, token: str) -> Optional[User]:
        """Проверка refresh токена"""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            user_id = payload.get("user_id")
            if user_id is None:
                return None
            
            # Проверяем, что токен существует в базе данных
            db_token = self.db.query(RefreshToken).filter(RefreshToken.token == token).first()
            if not db_token:
                return None
            
            # Проверяем, что токен не истек
            if db_token.expires_at < datetime.utcnow():
                self.db.delete(db_token)
                self.db.commit()
                return None
            
            # Получаем пользователя
            user = self.get_user_by_id(user_id)
            return user
            
        except JWTError:
            return None
    
    def revoke_refresh_token(self, token: str) -> bool:
        """Отзыв refresh токена"""
        db_token = self.db.query(RefreshToken).filter(RefreshToken.token == token).first()
        if db_token:
            self.db.delete(db_token)
            self.db.commit()
            return True
        return False
    
    def revoke_all_user_tokens(self, user_id: int) -> bool:
        """Отзыв всех refresh токенов пользователя"""
        self.db.query(RefreshToken).filter(RefreshToken.user_id == user_id).delete()
        self.db.commit()
        return True
