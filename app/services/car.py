"""
Сервис для работы с автомобилями
"""
from typing import List, Optional, Dict, Any, Tuple, Set
from sqlalchemy.orm import Session

from app.models.car import Car
from app.models.additional_service import AdditionalService
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

    def get_meta(self) -> Dict[str, Any]:
        """Агрегированные данные: типы топлива и диапазон цен"""
        cars: List[Car] = self.get_cars()
        fuel_types: Set[str] = set()
        prices: List[int] = []
        for car in cars:
            if car.fuel_type:
                fuel_types.add(car.fuel_type)
            if car.price is not None:
                prices.append(int(car.price))

        min_price: Optional[int] = min(prices) if prices else None
        max_price: Optional[int] = max(prices) if prices else None
        return {
            "fuel_types": sorted(list(fuel_types)),
            "min_price": min_price,
            "max_price": max_price,
        }

    def get_popular(self, limit: int = 8) -> List[Car]:
        """Популярные автомобили по рейтингу"""
        return (
            self.db.query(Car)
            .order_by(Car.rating.desc())
            .limit(limit)
            .all()
        )

    def get_car_services(self, car_id: int) -> List[AdditionalService]:
        """Получить дополнительные услуги для автомобиля (по id из car.additional_services)"""
        car = self.get_car_by_id(car_id)
        if not car or not car.additional_services:
            return []
        service_ids: List[int] = [int(sid) for sid in car.additional_services]
        return (
            self.db.query(AdditionalService)
            .filter(AdditionalService.id.in_(service_ids))
            .all()
        )
