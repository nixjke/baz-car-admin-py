#!/usr/bin/env python3
"""
Скрипт для создания пользователей через командную строку
Использование: python create_user.py <username> <password>
"""

import sys
import getpass
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.services.auth import AuthService
from app.schemas.user import UserCreate


def create_user(username: str, password: str) -> bool:
    """Создание нового пользователя"""
    db: Session = SessionLocal()
    try:
        auth_service = AuthService(db)
        
        # Проверяем, существует ли пользователь
        existing_user = auth_service.get_user_by_username(username)
        if existing_user:
            print(f"❌ Ошибка: Пользователь '{username}' уже существует!")
            return False
        
        # Создаем пользователя
        user_data = UserCreate(username=username, password=password)
        user = auth_service.create_user(user_data)
        
        print(f"✅ Пользователь '{username}' успешно создан!")
        print(f"   ID: {user.id}")
        print(f"   Username: {user.username}")
        print(f"   Role: {user.role}")
        print(f"   Active: {user.is_active}")
        print(f"   Created: {user.created_at}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при создании пользователя: {e}")
        return False
    finally:
        db.close()


def main():
    """Основная функция"""
    print("🔐 Создание нового пользователя")
    print("=" * 40)
    
    # Получаем аргументы командной строки
    if len(sys.argv) == 3:
        username = sys.argv[1]
        password = sys.argv[2]
    elif len(sys.argv) == 2:
        username = sys.argv[1]
        # Запрашиваем пароль интерактивно
        password = getpass.getpass("Введите пароль: ")
        if not password:
            print("❌ Пароль не может быть пустым!")
            return
    else:
        print("Использование:")
        print("  python create_user.py <username> <password>")
        print("  python create_user.py <username>  # пароль будет запрошен интерактивно")
        print()
        print("Примеры:")
        print("  python create_user.py admin mypassword123")
        print("  python create_user.py john")
        return
    
    # Валидация входных данных
    if not username or len(username.strip()) == 0:
        print("❌ Имя пользователя не может быть пустым!")
        return
    
    if len(username) < 3:
        print("❌ Имя пользователя должно содержать минимум 3 символа!")
        return
    
    if len(password) < 6:
        print("❌ Пароль должен содержать минимум 6 символов!")
        return
    
    # Создаем пользователя
    success = create_user(username.strip(), password)
    
    if success:
        print()
        print("🎉 Пользователь готов к использованию!")
        print("   Теперь можно войти в систему с этими учетными данными.")
    else:
        print()
        print("💥 Не удалось создать пользователя.")
        sys.exit(1)


if __name__ == "__main__":
    main()
