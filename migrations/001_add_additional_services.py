"""
Миграция: Добавление поля additional_services в таблицу cars
Описание: Добавляет колонку additional_services для хранения дополнительных услуг автомобиля
"""
import sqlite3
from pathlib import Path


def migrate() -> bool:
    """Выполняет миграцию"""
    db_path = Path("baz_car.db")
    
    if not db_path.exists():
        print("❌ База данных не найдена!")
        return False
    
    try:
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
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при миграции: {e}")
        if 'conn' in locals():
            conn.close()
        return False
