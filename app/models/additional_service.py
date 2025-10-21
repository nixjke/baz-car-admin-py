"""
Модель дополнительных услуг
"""
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class AdditionalService(Base):
    """Модель дополнительной услуги"""
    __tablename__ = "additional_services"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(String(50), unique=True, index=True, nullable=False)  # youngDriver, childSeat, etc.
    label = Column(String(200), nullable=False)  # Название услуги
    description = Column(Text, nullable=True)  # Описание услуги
    fee = Column(Float, nullable=False, default=0.0)  # Стоимость услуги
    fee_type = Column(String(20), nullable=False, default="fixed")  # fixed, percentage
    icon_key = Column(String(50), nullable=True)  # Ключ иконки
    is_active = Column(Boolean, default=True)  # Активна ли услуга
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
