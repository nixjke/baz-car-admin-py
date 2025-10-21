#!/usr/bin/env python3
"""
Скрипт для проверки статуса миграций
"""
import sys
from migrations._migration_manager import MigrationManager


def main():
    """Проверяет статус миграций"""
    print("📊 Статус миграций Baz Car API")
    print("=" * 40)
    
    manager = MigrationManager()
    
    # Создаем таблицу миграций если её нет
    manager.create_migrations_table()
    
    # Получаем статус
    status = manager.get_migration_status()
    
    print(f"📈 Общая статистика:")
    print(f"   Всего доступно миграций: {status['total_available']}")
    print(f"   Выполнено миграций: {status['executed']}")
    print(f"   Ожидает выполнения: {status['pending']}")
    
    if status['executed'] > 0:
        print(f"\n✅ Выполненные миграции:")
        for migration in status['executed_migrations']:
            print(f"   ✓ {migration}")
    
    if status['pending'] > 0:
        print(f"\n⏳ Ожидающие миграции:")
        for migration in status['pending_migrations']:
            print(f"   ○ {migration}")
        
        print(f"\n💡 Для выполнения миграций запустите:")
        print(f"   ./auto_migrate.sh")
    else:
        print(f"\n🎉 Все миграции выполнены!")
        print(f"   База данных актуальна")
    
    print(f"\n📁 Файл базы данных: baz_car.db")
    print(f"📋 История миграций: migrations_history")


if __name__ == "__main__":
    main()
