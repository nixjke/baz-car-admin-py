"""
Эндпоинт бронирования: расчет итоговой цены и генерация WhatsApp ссылки
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.car import CarService
from app.models.car import Car
from app.models.additional_service import AdditionalService


router = APIRouter()


class BookingRequest(BaseModel):
    car_id: int
    pickup_date: str  # YYYY-MM-DD
    return_date: str  # YYYY-MM-DD
    delivery_option_id: Optional[str] = None  # "pickup" | "city" | "airport"
    additional_service_ids: Optional[List[str]] = Field(default_factory=list)  # service_id из БД
    customer_name: str
    customer_phone: str
    customer_email: Optional[str] = None


class BookingResponse(BaseModel):
    total_price: int
    rental_days: int
    daily_price: int
    whatsapp_link: str
    breakdown: Dict[str, Any]


# Локальная конфигурация опций доставки (портируется с фронта)
DELIVERY_OPTIONS: Dict[str, Dict[str, Any]] = {
    "pickup": {"id": "pickup", "label": "Самовывоз", "price": 0},
    "city": {"id": "city", "label": "Доставка по городу", "price": 700},
    "airport": {"id": "airport", "label": "Доставка в аэропорт", "price": 1000},
}

# Номер WhatsApp для связи (можно вынести в настройки позже)
WHATSAPP_NUMBER = "79894413888"


def _parse_days(pickup_date: str, return_date: str) -> int:
    from datetime import datetime
    fmt = "%Y-%m-%d"
    start = datetime.strptime(pickup_date, fmt)
    end = datetime.strptime(return_date, fmt)
    if end <= start:
        raise ValueError("Дата возврата должна быть позже даты получения")
    diff = end - start
    return max(1, diff.days)


@router.post("/", response_model=BookingResponse)
def create_booking(
    data: BookingRequest,
    db: Session = Depends(get_db),
):
    """Рассчитать стоимость, собрать текст и вернуть ссылку WhatsApp"""
    car_service = CarService(db)
    car: Optional[Car] = car_service.get_car_by_id(data.car_id)
    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Автомобиль не найден")

    try:
        rental_days = _parse_days(data.pickup_date, data.return_date)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # Цена за день с учетом скидки от 3 дней
    daily_price = car.price or 0
    if rental_days >= 3 and car.price_3plus_days:
        daily_price = car.price_3plus_days

    rental_cost = (daily_price or 0) * rental_days

    # Доставка
    delivery_price = 0
    delivery_label = None
    if data.delivery_option_id:
        opt = DELIVERY_OPTIONS.get(data.delivery_option_id)
        if opt:
            delivery_price = int(opt.get("price", 0))
            delivery_label = opt.get("label")

    # Доп. услуги: выбираем по service_id, считаем fee (fixed), игнорируем неактивные
    additional_services: List[AdditionalService] = []
    additional_total = 0
    selected_ids = data.additional_service_ids or []
    if selected_ids:
        additional_services = (
            db.query(AdditionalService)
            .filter(AdditionalService.service_id.in_(selected_ids))
            .all()
        )
        for s in additional_services:
            if not s.is_active:
                continue
            fee = int(s.fee or 0)
            # Если понадобится поддержка fee_type == 'percentage' или 'daily'
            if s.fee_type == "percentage":
                additional_total += int(rental_cost * (fee / 100.0))
            elif s.fee_type == "daily":
                additional_total += fee * rental_days
            else:
                additional_total += fee

    total_price = int(rental_cost + delivery_price + additional_total)

    # Сообщение для WhatsApp
    lines: List[str] = []
    lines.append("Здравствуйте! Я хочу оформить заказ на аренду автомобиля:\n")
    lines.append(f"Модель: {car.name}\n")
    lines.append(f"Период: {data.pickup_date} - {data.return_date}\n")
    lines.append(f"Стоимость аренды: {rental_cost:,} ₽".replace(",", "\u00a0"))
    if delivery_label and delivery_price > 0:
        lines.append(f"Доставка: {delivery_label} (+{delivery_price:,} ₽)".replace(",", "\u00a0"))

    if additional_services:
        lines.append("Доп. услуги:")
        for s in additional_services:
            if not s.is_active:
                continue
            # Отобразим как фиксированную стоимость для простоты
            lines.append(f" - {s.label}: +{int(s.fee):,} ₽".replace(",", "\u00a0"))

    lines.append("")
    lines.append(f"Итого: {total_price:,} ₽".replace(",", "\u00a0"))
    lines.append("")
    lines.append("Контактная информация:")
    lines.append(f"Имя: {data.customer_name}")
    lines.append(f"Телефон: {data.customer_phone}")
    if data.customer_email:
        lines.append(f"Email: {data.customer_email}")

    message = "\n".join(lines)

    # Формируем ссылку
    from urllib.parse import quote
    whatsapp_link = f"https://wa.me/{WHATSAPP_NUMBER}?text={quote(message)}"

    return BookingResponse(
        total_price=total_price,
        rental_days=rental_days,
        daily_price=int(daily_price or 0),
        whatsapp_link=whatsapp_link,
        breakdown={
            "rental_cost": rental_cost,
            "delivery_price": delivery_price,
            "additional_total": additional_total,
        },
    )


