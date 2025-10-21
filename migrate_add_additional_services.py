#!/usr/bin/env python3
"""
Миграция для добавления поля additional_services в таблицу cars
"""

import sqlite3
import os
from pathlib import Path

def migrate_database():
    """Добавляет колонку additional_services в таблицу cars"""
    
    # Путь к базе данных
    db_path = Path("baz_car.db")
    
    if not db_path.exists():
        print("❌ База данных не найдена!")
        return False
    
    try:
        # Подключаемся к базе данных
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверяем, существует ли уже колонка
        cursor.execute("PRAGMA table_info(cars)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'additional_services' in columns:
            print("✅ Колонка 'additional_services' уже существует в таблице cars")
            conn.close()
            return True
        
        print("🔄 Добавляем колонку 'additional_services' в таблицу cars...")
        
        # Добавляем колонку additional_services
        cursor.execute("""
            ALTER TABLE cars 
            ADD COLUMN additional_services TEXT DEFAULT '[]'
        """)
        
        # Обновляем существующие записи, устанавливая пустой JSON массив
        cursor.execute("""
            UPDATE cars 
            SET additional_services = '[]' 
            WHERE additional_services IS NULL
        """)
        
        # Сохраняем изменения
        conn.commit()
        
        print("✅ Колонка 'additional_services' успешно добавлена!")
        print("✅ Существующие записи обновлены с пустым массивом услуг")
        
        # Проверяем результат
        cursor.execute("PRAGMA table_info(cars)")
        columns = cursor.fetchall()
        
        print("\n📋 Структура таблицы cars:")
        for column in columns:
            print(f"   - {column[1]} ({column[2]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при миграции: {e}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    print("🔧 Миграция базы данных: добавление additional_services")
    print("=" * 60)
    
    success = migrate_database()
    
    if success:
        print("\n🎉 Миграция завершена успешно!")
        print("   Теперь можно запускать сервер.")
    else:
        print("\n💥 Миграция не удалась!")
        print("   Проверьте ошибки выше.")
