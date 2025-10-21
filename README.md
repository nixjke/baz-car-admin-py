# Baz Car Admin API - Python FastAPI

Этот проект представляет собой API для управления автомобилями, перенесенный с Go на Python с использованием FastAPI.

## Структура проекта

```
baz-car-py/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── auth.py      # Эндпоинты аутентификации
│   │       │   └── cars.py      # Эндпоинты автомобилей
│   │       └── api.py           # Основной роутер API
│   ├── core/
│   │   ├── config.py            # Конфигурация приложения
│   │   └── database.py          # Настройка базы данных
│   ├── models/
│   │   ├── user.py              # Модель пользователя
│   │   ├── car.py               # Модель автомобиля
│   │   └── refresh_token.py     # Модель refresh токена
│   ├── schemas/
│   │   ├── user.py              # Схемы пользователей
│   │   └── car.py               # Схемы автомобилей
│   └── services/
│       ├── auth.py              # Сервис аутентификации
│       ├── car.py               # Сервис автомобилей
│       └── storage.py           # Сервис файлов
├── main.py                      # Точка входа
├── requirements.txt             # Зависимости
└── README.md                    # Документация
```

## Установка и запуск

### Быстрый старт

Используйте скрипт для автоматической установки и запуска:
```bash
./start.sh
```

### Ручная установка

1. Создайте виртуальное окружение:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Скопируйте файл конфигурации:
```bash
cp env.example .env
```

4. Инициализируйте базу данных:
```bash
python init_db.py
```

5. Запустите сервер:
```bash
python main.py
```

Или с помощью uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

Сервер будет доступен по адресу `http://localhost:8080`

### Тестирование API

Запустите тестовый скрипт:
```bash
python test_api.py
```

### Документация API

После запуска сервера документация API будет доступна по адресам:
- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

## API Эндпоинты

### Аутентификация

- `POST /api/v1/auth/register` - Регистрация пользователя
- `POST /api/v1/auth/login` - Вход пользователя
- `POST /api/v1/auth/refresh` - Обновление токена
- `POST /api/v1/auth/logout` - Выход пользователя
- `GET /api/v1/auth/profile` - Получение профиля

### Автомобили

- `GET /api/v1/cars` - Список автомобилей
- `GET /api/v1/cars/{id}` - Получение автомобиля по ID
- `POST /api/v1/cars` - Создание автомобиля
- `PUT/PATCH /api/v1/cars/{id}` - Обновление автомобиля
- `DELETE /api/v1/cars/{id}` - Удаление автомобиля
- `POST /api/v1/cars/{id}/images` - Загрузка изображений
- `POST /api/v1/cars/uploads/temp` - Временная загрузка файлов
- `POST /api/v1/cars/uploads/cleanup` - Очистка файлов

### Общие

- `GET /` - Информация об API
- `GET /health` - Проверка состояния

## Примеры использования

### Регистрация пользователя
```bash
curl -X POST http://localhost:8080/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "first_name": "Тест",
    "last_name": "Пользователь"
  }'
```

### Авторизация
```bash
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### Получение списка автомобилей
```bash
curl -X GET http://localhost:8080/api/v1/cars \
  -H "Authorization: Bearer <your-jwt-token>"
```

### Создание автомобиля
```bash
curl -X POST http://localhost:8080/api/v1/cars \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Toyota Camry",
    "category": "sedan",
    "price": 5000,
    "description": "Комфортный седан"
  }'
```

## Особенности

- **FastAPI**: Современный веб-фреймворк с автоматической документацией
- **SQLAlchemy**: ORM для работы с базой данных
- **JWT токены**: Аутентификация с access и refresh токенами
- **SQLite база данных**: Легкая в использовании база данных
- **Хеширование паролей**: Используется bcrypt для безопасности
- **Загрузка файлов**: Поддержка загрузки изображений автомобилей
- **CORS**: Настроена поддержка CORS запросов
- **Валидация данных**: Автоматическая валидация с Pydantic

## Переменные окружения

- `JWT_SECRET_KEY` - Секретный ключ для JWT токенов
- `DATABASE_URL` - URL базы данных
- `UPLOAD_DIR` - Директория для загрузки файлов
- `MAX_FILE_SIZE` - Максимальный размер файла

## Безопасность

⚠️ **Важно**: В продакшене обязательно установите переменную окружения `JWT_SECRET_KEY` с надежным секретным ключом.

## Документация API

После запуска сервера документация API будет доступна по адресам:
- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`
