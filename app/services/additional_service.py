"""
Сервис для работы с дополнительными услугами
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.additional_service import AdditionalService
from app.schemas.additional_service import AdditionalServiceCreate, AdditionalServiceUpdate


class AdditionalServiceService:
    """Сервис для работы с дополнительными услугами"""

    @staticmethod
    def get_services(db: Session, skip: int = 0, limit: int = 100) -> List[AdditionalService]:
        """Получить список всех дополнительных услуг"""
        return db.query(AdditionalService).offset(skip).limit(limit).all()

    @staticmethod
    def get_service(db: Session, service_id: int) -> Optional[AdditionalService]:
        """Получить дополнительную услугу по ID"""
        return db.query(AdditionalService).filter(AdditionalService.id == service_id).first()

    @staticmethod
    def get_service_by_service_id(db: Session, service_id: str) -> Optional[AdditionalService]:
        """Получить дополнительную услугу по service_id"""
        return db.query(AdditionalService).filter(AdditionalService.service_id == service_id).first()

    @staticmethod
    def create_service(db: Session, service: AdditionalServiceCreate) -> AdditionalService:
        """Создать новую дополнительную услугу"""
        db_service = AdditionalService(**service.dict())
        db.add(db_service)
        db.commit()
        db.refresh(db_service)
        return db_service

    @staticmethod
    def update_service(db: Session, service_id: int, service: AdditionalServiceUpdate) -> Optional[AdditionalService]:
        """Обновить дополнительную услугу"""
        db_service = db.query(AdditionalService).filter(AdditionalService.id == service_id).first()
        if not db_service:
            return None
        
        update_data = service.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_service, field, value)
        
        db.commit()
        db.refresh(db_service)
        return db_service

    @staticmethod
    def delete_service(db: Session, service_id: int) -> bool:
        """Удалить дополнительную услугу"""
        db_service = db.query(AdditionalService).filter(AdditionalService.id == service_id).first()
        if not db_service:
            return False
        
        db.delete(db_service)
        db.commit()
        return True

    @staticmethod
    def get_active_services(db: Session) -> List[AdditionalService]:
        """Получить только активные дополнительные услуги"""
        return db.query(AdditionalService).filter(AdditionalService.is_active == True).all()
