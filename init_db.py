"""
Скрипт для инициализации базы данных
"""
import asyncio
from app.core.database import init_db


async def main():
    """Инициализация базы данных"""
    print("Инициализация базы данных...")
    await init_db()
    print("База данных инициализирована успешно!")


if __name__ == "__main__":
    asyncio.run(main())
