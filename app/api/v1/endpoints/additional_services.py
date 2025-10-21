"""
API endpoints для дополнительных услуг
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.additional_service import AdditionalService
from app.schemas.additional_service import (
    AdditionalService as AdditionalServiceSchema,
    AdditionalServiceCreate,
    AdditionalServiceUpdate
)
from app.services.additional_service import AdditionalServiceService
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[AdditionalServiceSchema])
def get_additional_services(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получить список всех дополнительных услуг"""
    services = AdditionalServiceService.get_services(db, skip=skip, limit=limit)
    return services


@router.get("/active", response_model=List[AdditionalServiceSchema])
def get_active_additional_services(
    db: Session = Depends(get_db)
):
    """Получить только активные дополнительные услуги"""
    services = AdditionalServiceService.get_active_services(db)
    return services


@router.get("/{service_id}", response_model=AdditionalServiceSchema)
def get_additional_service(
    service_id: int,
    db: Session = Depends(get_db)
):
    """Получить дополнительную услугу по ID"""
    service = AdditionalServiceService.get_service(db, service_id=service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Дополнительная услуга не найдена"
        )
    return service


@router.post("/", response_model=AdditionalServiceSchema)
def create_additional_service(
    service: AdditionalServiceCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Создать новую дополнительную услугу (требует авторизации)"""
    # Проверяем, не существует ли уже услуга с таким service_id
    existing_service = AdditionalServiceService.get_service_by_service_id(db, service.service_id)
    if existing_service:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Услуга с таким service_id уже существует"
        )
    
    return AdditionalServiceService.create_service(db, service)


@router.put("/{service_id}", response_model=AdditionalServiceSchema)
def update_additional_service(
    service_id: int,
    service: AdditionalServiceUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Обновить дополнительную услугу (требует авторизации)"""
    updated_service = AdditionalServiceService.update_service(db, service_id, service)
    if not updated_service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Дополнительная услуга не найдена"
        )
    return updated_service


@router.delete("/{service_id}")
def delete_additional_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Удалить дополнительную услугу (требует авторизации)"""
    success = AdditionalServiceService.delete_service(db, service_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Дополнительная услуга не найдена"
        )
    return {"message": "Дополнительная услуга успешно удалена"}
