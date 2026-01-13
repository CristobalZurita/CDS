"""
Pydantic schemas para cotizaciones
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class QuoteStatus(str, Enum):
    """Estados de cotización"""
    PENDING = "pending"
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


class QuoteItemType(str, Enum):
    """Tipos de items en cotización"""
    FAULT_REPAIR = "fault_repair"
    PART_REPLACEMENT = "part_replacement"
    LABOR = "labor"
    DIAGNOSTIC_FEE = "diagnostic_fee"
    OTHER = "other"


class QuoteItemBase(BaseModel):
    """Item individual de cotización"""
    type: QuoteItemType
    description: str
    quantity: int = Field(default=1, ge=1)
    unit_price: int = Field(..., description="Precio unitario en centavos")
    total_price: int = Field(..., description="Precio total en centavos")


class QuoteBase(BaseModel):
    """Schema base para cotizaciones"""
    diagnostic_id: Optional[int] = None
    repair_id: Optional[int] = None
    instrument_brand: str
    instrument_model: str
    instrument_value: Optional[int] = Field(None, description="Valor estimado del instrumento en centavos")
    items: List[QuoteItemBase]
    subtotal: int = Field(..., description="Subtotal en centavos")
    labor_hours: Optional[int] = Field(None, ge=0)
    labor_cost: Optional[int] = Field(None, description="Costo de mano de obra en centavos")
    total: int = Field(..., description="Total en centavos")
    min_price: Optional[int] = Field(None, description="Precio mínimo estimado en centavos")
    max_price: Optional[int] = Field(None, description="Precio máximo estimado en centavos")
    validity_days: int = Field(default=30, ge=1)
    notes: Optional[str] = None
    disclaimer: Optional[str] = None


class QuoteCreate(QuoteBase):
    """Schema para crear cotización"""
    pass


class QuoteUpdate(BaseModel):
    """Schema para actualizar cotización"""
    status: Optional[QuoteStatus] = None
    notes: Optional[str] = None
    total: Optional[int] = None
    validity_days: Optional[int] = Field(None, ge=1)


class QuoteResponse(BaseModel):
    """Schema para respuesta de cotización"""
    id: int
    diagnostic_id: Optional[int]
    repair_id: Optional[int]
    instrument_brand: str
    instrument_model: str
    status: QuoteStatus
    total: int
    min_price: Optional[int]
    max_price: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QuoteDetail(QuoteResponse):
    """Schema para respuesta detallada de cotización"""
    instrument_value: Optional[int]
    items: List[QuoteItemBase]
    subtotal: int
    labor_hours: Optional[int]
    labor_cost: Optional[int]
    validity_days: int
    notes: Optional[str]
    disclaimer: Optional[str]

    class Config:
        from_attributes = True


class QuoteEstimateRequest(BaseModel):
    """Schema para solicitud de estimación de cotización"""
    instrument_id: str
    brand_id: str
    faults: List[str] = Field(..., min_items=1)
    client_notes: Optional[str] = None


class QuoteEstimateResponse(BaseModel):
    """Schema para respuesta de estimación de cotización"""
    instrument_brand: str
    instrument_model: str
    instrument_tier: str
    instrument_value_avg: int
    faults: List[str]
    base_total: int
    complexity_multiplier: float
    value_multiplier: float
    adjusted_total: int
    min_price: int
    max_price: int
    labor_hours: int
    breakdown: List[Dict[str, Any]]
    max_recommended: int
    exceeds_recommendation: bool
    disclaimer: str
