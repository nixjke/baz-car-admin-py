"""
Скрипт для инициализации базовых дополнительных услуг
"""
import asyncio
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, init_db
from app.models.additional_service import AdditionalService
from app.schemas.additional_service import AdditionalServiceCreate


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


def init_additional_services():
    """Инициализация дополнительных услуг"""
    db = SessionLocal()
    try:
        # Проверяем, есть ли уже услуги в базе
        existing_services = db.query(AdditionalService).count()
        if existing_services > 0:
            print(f"В базе уже есть {existing_services} дополнительных услуг. Пропускаем инициализацию.")
            return

        # Создаем базовые услуги
        for service_data in DEFAULT_SERVICES:
            service = AdditionalService(**service_data)
            db.add(service)
        
        db.commit()
        print(f"Успешно создано {len(DEFAULT_SERVICES)} дополнительных услуг:")
        for service_data in DEFAULT_SERVICES:
            print(f"  - {service_data['label']} ({service_data['service_id']})")
            
    except Exception as e:
        print(f"Ошибка при создании дополнительных услуг: {e}")
        db.rollback()
    finally:
        db.close()


async def main():
    """Основная функция"""
    print("Инициализация базы данных...")
    await init_db()
    
    print("Инициализация дополнительных услуг...")
    init_additional_services()
    
    print("Готово!")


if __name__ == "__main__":
    asyncio.run(main())
