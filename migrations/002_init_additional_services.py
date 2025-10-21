"""
Миграция: Инициализация базовых дополнительных услуг
Описание: Создает базовые дополнительные услуги в системе
"""
import sqlite3
from pathlib import Path


# Базовые дополнительные услуги
DEFAULT_SERVICES = [
    {
        "service_id": "youngDriver",
        "label": "Молодой водитель (18-21 год)",
        "description": "Дополнительная опция для водителей в возрасте от 18 до 21 года. Обеспечивает полное страховое покрытие.",
        "fee": 5000.0,
        "fee_type": "fixed",
        "icon_key": "User",
        "is_active": True
    },
    {
        "service_id": "childSeat",
        "label": "Детское кресло",
        "description": "Безопасность и комфорт для ваших маленьких пассажиров. Устанавливается по запросу.",
        "fee": 700.0,
        "fee_type": "fixed",
        "icon_key": "Baby",
        "is_active": True
    },
    {
        "service_id": "personalDriver",
        "label": "Личный водитель",
        "description": "Наслаждайтесь поездкой, доверив управление профессионалу. Идеально для деловых поездок или экскурсий.",
        "fee": 6000.0,
        "fee_type": "fixed",
        "icon_key": "UserCheck",
        "is_active": True
    },
    {
        "service_id": "ps5",
        "label": "PlayStation 5",
        "description": "Развлечения в дороге для детей и взрослых. В вашем распоряжении PS5 с предустановленной коллекцией популярных игр - готовые решения для любого настроения!",
        "fee": 1000.0,
        "fee_type": "fixed",
        "icon_key": "Gamepad2",
        "is_active": True
    },
    {
        "service_id": "transmission",
        "label": "Передача руля",
        "description": "Возможность передать управление автомобилем другому водителю. Идеально для длительных поездок с компанией.",
        "fee": 4000.0,
        "fee_type": "fixed",
        "icon_key": "Settings",
        "is_active": True
    }
]


def migrate() -> bool:
    """Выполняет миграцию"""
    db_path = Path("baz_car.db")
    
    if not db_path.exists():
        print("❌ База данных не найдена!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверяем, есть ли уже услуги в базе
        cursor.execute("SELECT COUNT(*) FROM additional_services")
        existing_count = cursor.fetchone()[0]
        
        if existing_count > 0:
            print(f"✅ В базе уже есть {existing_count} дополнительных услуг. Пропускаем инициализацию.")
            conn.close()
            return True
        
        print("🔄 Создаем базовые дополнительные услуги...")
        
        # Создаем базовые услуги
        for service_data in DEFAULT_SERVICES:
            cursor.execute("""
                INSERT INTO additional_services 
                (service_id, label, description, fee, fee_type, icon_key, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            """, (
                service_data['service_id'],
                service_data['label'],
                service_data['description'],
                service_data['fee'],
                service_data['fee_type'],
                service_data['icon_key'],
                service_data['is_active']
            ))
        
        # Сохраняем изменения
        conn.commit()
        
        print(f"✅ Успешно создано {len(DEFAULT_SERVICES)} дополнительных услуг:")
        for service_data in DEFAULT_SERVICES:
            print(f"   - {service_data['label']} ({service_data['service_id']})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при миграции: {e}")
        if 'conn' in locals():
            conn.close()
        return False
