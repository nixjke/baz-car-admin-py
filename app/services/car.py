"""
Сервис для работы с автомобилями
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.car import Car
from app.schemas.car import CarCreate, CarUpdate


class CarService:
    """Сервис для работы с автомобилями"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_cars(self) -> List[Car]:
        """Получение списка всех автомобилей"""
        return self.db.query(Car).all()
    
    def get_car_by_id(self, car_id: int) -> Optional[Car]:
        """Получение автомобиля по ID"""
        return self.db.query(Car).filter(Car.id == car_id).first()
    
    def create_car(self, car_data: CarCreate) -> Car:
        """Создание нового автомобиля"""
        db_car = Car(**car_data.dict())
        self.db.add(db_car)
        self.db.commit()
        self.db.refresh(db_car)
        return db_car
    
    def update_car(self, car_id: int, car_data: CarUpdate) -> Optional[Car]:
        """Обновление автомобиля"""
        db_car = self.get_car_by_id(car_id)
        if not db_car:
            return None
        
        # Обновляем только переданные поля
        update_data = car_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_car, field, value)
        
        self.db.commit()
        self.db.refresh(db_car)
        return db_car
    
    def delete_car(self, car_id: int) -> bool:
        """Удаление автомобиля"""
        db_car = self.get_car_by_id(car_id)
        if not db_car:
            return False
        
        self.db.delete(db_car)
        self.db.commit()
        return True
    
    def update_car_images(self, car_id: int, images: List[str]) -> Optional[Car]:
        """Обновление изображений автомобиля"""
        db_car = self.get_car_by_id(car_id)
        if not db_car:
            return None
        
        db_car.images = images
        self.db.commit()
        self.db.refresh(db_car)
        return db_car
