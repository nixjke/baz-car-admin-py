"""
API эндпоинты для автомобилей
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.car import CarService
from app.services.storage import StorageService
from app.schemas.car import Car, CarCreate, CarUpdate, UploadResponse, CleanupResponse
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.user import User

router = APIRouter()


def get_car_service(db: Session = Depends(get_db)) -> CarService:
    """Получение сервиса автомобилей"""
    return CarService(db)


def get_storage_service() -> StorageService:
    """Получение сервиса файлов"""
    return StorageService()


@router.get("/", response_model=List[Car])
async def get_cars(
    car_service: CarService = Depends(get_car_service)
):
    """Получение списка всех автомобилей"""
    cars = car_service.get_cars()
    return cars


@router.get("/meta")
async def get_cars_meta(
    car_service: CarService = Depends(get_car_service)
) -> Dict[str, Any]:
    """Агрегированные данные для фильтров (типы топлива, диапазон цен)"""
    return car_service.get_meta()


@router.get("/popular", response_model=List[Car])
async def get_popular_cars(
    limit: int = 8,
    car_service: CarService = Depends(get_car_service)
):
    """Популярные автомобили по рейтингу"""
    return car_service.get_popular(limit=limit)


@router.get("/{car_id}", response_model=Car)
async def get_car(
    car_id: int,
    car_service: CarService = Depends(get_car_service)
):
    """Получение автомобиля по ID"""
    car = car_service.get_car_by_id(car_id)
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Автомобиль не найден"
        )
    return car


@router.post("/", response_model=Car, status_code=status.HTTP_201_CREATED)
async def create_car(
    car_data: CarCreate,
    car_service: CarService = Depends(get_car_service),
    storage_service: StorageService = Depends(get_storage_service),
    current_user: User = Depends(get_current_user)
):
    """Создание нового автомобиля"""
    try:
        # Создаем автомобиль
        car = car_service.create_car(car_data)
        
        # Если есть временные изображения, перемещаем их
        if car_data.images:
            temp_images = [img for img in car_data.images if "/uploads/temp/" in img]
            if temp_images:
                moved_images = storage_service.move_temp_to_car(car.id, temp_images)
                # Обновляем изображения автомобиля
                car_service.update_car_images(car.id, moved_images)
                car = car_service.get_car_by_id(car.id)
        
        return car
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{car_id}", response_model=Car)
@router.patch("/{car_id}", response_model=Car)
async def update_car(
    car_id: int,
    car_data: CarUpdate,
    car_service: CarService = Depends(get_car_service),
    current_user: User = Depends(get_current_user)
):
    """Обновление автомобиля"""
    car = car_service.update_car(car_id, car_data)
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Автомобиль не найден"
        )
    return car


@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_car(
    car_id: int,
    car_service: CarService = Depends(get_car_service),
    current_user: User = Depends(get_current_user)
):
    """Удаление автомобиля"""
    success = car_service.delete_car(car_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Автомобиль не найден"
        )


@router.post("/{car_id}/images", response_model=UploadResponse)
async def upload_car_images(
    car_id: int,
    files: List[UploadFile] = File(...),
    car_service: CarService = Depends(get_car_service),
    storage_service: StorageService = Depends(get_storage_service),
    current_user: User = Depends(get_current_user)
):
    """Загрузка изображений для автомобиля"""
    # Проверяем, что автомобиль существует
    car = car_service.get_car_by_id(car_id)
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Автомобиль не найден"
        )
    
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Файлы не предоставлены"
        )
    
    uploaded_paths = []
    for file in files:
        try:
            path = storage_service.save_file(car_id, file)
            uploaded_paths.append(path)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ошибка загрузки файла {file.filename}: {str(e)}"
            )
    
    # Обновляем список изображений автомобиля
    current_images = car.images or []
    new_images = current_images + uploaded_paths
    car_service.update_car_images(car_id, new_images)
    
    return UploadResponse(uploaded=uploaded_paths)


@router.post("/uploads/temp", response_model=UploadResponse)
async def upload_temp_files(
    files: List[UploadFile] = File(...),
    storage_service: StorageService = Depends(get_storage_service),
    current_user: User = Depends(get_current_user)
):
    """Загрузка временных файлов"""
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Файлы не предоставлены"
        )
    
    uploaded_paths = []
    for file in files:
        try:
            path = storage_service.save_temp_file(file)
            uploaded_paths.append(path)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ошибка загрузки файла {file.filename}: {str(e)}"
            )
    
    return UploadResponse(uploaded=uploaded_paths)


@router.post("/uploads/cleanup", response_model=CleanupResponse)
async def cleanup_uploads(
    paths: List[str],
    storage_service: StorageService = Depends(get_storage_service),
    current_user: User = Depends(get_current_user)
):
    """Очистка загруженных файлов"""
    if not paths:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пути не предоставлены"
        )
    
    deleted_count = storage_service.delete_by_public_paths(paths)
    return CleanupResponse(deleted=deleted_count)


@router.get("/{car_id}/services")
async def get_car_services(
    car_id: int,
    car_service: CarService = Depends(get_car_service)
) -> List[dict]:
    """Получить активные дополнительные услуги, доступные для автомобиля"""
    services = car_service.get_car_services(car_id)
    # Возвращаем как словари для совместимости
    return [
        {
            "id": s.id,
            "service_id": s.service_id,
            "label": s.label,
            "description": s.description,
            "fee": s.fee,
            "fee_type": s.fee_type,
            "icon_key": s.icon_key,
            "is_active": s.is_active,
            "created_at": s.created_at,
            "updated_at": s.updated_at,
        }
        for s in services if s.is_active
    ]
