"""
Pydantic schemas para reparaciones
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from backend.app.models.repair import RepairStatus


class RepairBase(BaseModel):
    """Schema base para reparaciones"""
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    instrument_id: Optional[int] = None
    estimated_price: Optional[int] = None  # en centavos
    estimated_days: Optional[int] = None
    notes: Optional[str] = None
    is_priority: bool = False


class RepairCreate(RepairBase):
    """Schema para crear reparación"""
    client_id: int


class RepairUpdate(BaseModel):
    """Schema para actualizar reparación"""
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    instrument_id: Optional[int] = None
    estimated_price: Optional[int] = None
    estimated_days: Optional[int] = None
    final_price: Optional[int] = None
    notes: Optional[str] = None
    is_priority: Optional[bool] = None


class RepairStatusUpdate(BaseModel):
    """Schema para cambiar estado de reparación"""
    status: RepairStatus
    notes: Optional[str] = None


class RepairNoteCreate(BaseModel):
    """Schema para agregar nota a reparación"""
    note: str = Field(..., min_length=1)


class RepairResponse(BaseModel):
    """Schema para respuesta básica de reparación"""
    id: int
    client_id: int
    instrument_id: Optional[int]
    title: str
    description: Optional[str]
    status: RepairStatus
    estimated_price: Optional[int]
    final_price: Optional[int]
    estimated_days: Optional[int]
    is_priority: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RepairDetail(RepairResponse):
    """Schema para respuesta detallada de reparación (con relaciones)"""
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    notes: Optional[str]

    class Config:
        from_attributes = True


class RepairStats(BaseModel):
    """Schema para estadísticas de reparaciones"""
    total: int
    pending: int
    in_progress: int
    waiting_parts: int
    completed: int
    ready_pickup: int
    delivered: int
    cancelled: int
