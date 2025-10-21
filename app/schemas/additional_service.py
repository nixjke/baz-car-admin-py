"""
Схемы для дополнительных услуг
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AdditionalServiceBase(BaseModel):
    """Базовая схема дополнительной услуги"""
    service_id: str
    label: str
    description: Optional[str] = None
    fee: float
    fee_type: str = "fixed"
    icon_key: Optional[str] = None
    is_active: bool = True


class AdditionalServiceCreate(AdditionalServiceBase):
    """Схема для создания дополнительной услуги"""
    pass


class AdditionalServiceUpdate(BaseModel):
    """Схема для обновления дополнительной услуги"""
    service_id: Optional[str] = None
    label: Optional[str] = None
    description: Optional[str] = None
    fee: Optional[float] = None
    fee_type: Optional[str] = None
    icon_key: Optional[str] = None
    is_active: Optional[bool] = None


class AdditionalService(AdditionalServiceBase):
    """Схема дополнительной услуги"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
