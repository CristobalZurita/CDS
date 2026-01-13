"""
Pydantic schemas para diagnósticos
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class DiagnosticBase(BaseModel):
    """Schema base para diagnósticos"""
    repair_id: Optional[int] = None
    image_path: Optional[str] = Field(None, max_length=500)
    ai_analysis: Optional[Dict[str, Any]] = None
    detected_faults: Optional[List[Dict[str, Any]]] = None
    ai_confidence: int = Field(default=0, ge=0, le=100)
    quote_total: Optional[int] = Field(None, description="Total en centavos")
    quote_breakdown: Optional[Dict[str, Any]] = None
    labor_hours: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None


class DiagnosticCreate(DiagnosticBase):
    """Schema para crear diagnóstico"""
    pass


class DiagnosticUpdate(BaseModel):
    """Schema para actualizar diagnóstico"""
    repair_id: Optional[int] = None
    image_path: Optional[str] = Field(None, max_length=500)
    ai_analysis: Optional[Dict[str, Any]] = None
    detected_faults: Optional[List[Dict[str, Any]]] = None
    ai_confidence: Optional[int] = Field(None, ge=0, le=100)
    quote_total: Optional[int] = None
    quote_breakdown: Optional[Dict[str, Any]] = None
    labor_hours: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None


class DiagnosticResponse(BaseModel):
    """Schema para respuesta básica de diagnóstico"""
    id: int
    repair_id: Optional[int]
    image_path: Optional[str]
    ai_confidence: int
    quote_total: Optional[int]
    labor_hours: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DiagnosticDetail(DiagnosticResponse):
    """Schema para respuesta detallada de diagnóstico"""
    ai_analysis: Optional[Dict[str, Any]]
    detected_faults: Optional[List[Dict[str, Any]]]
    quote_breakdown: Optional[Dict[str, Any]]
    notes: Optional[str]

    class Config:
        from_attributes = True


class DiagnosticCalculateRequest(BaseModel):
    """Schema para solicitud de cálculo de cotización"""
    instrument_id: str
    brand_id: str
    faults: List[str]
    additional_notes: Optional[str] = None


class FaultBreakdown(BaseModel):
    """Desglose de una falla"""
    fault_id: str
    name: str
    base_price: int
    severity: Optional[int] = Field(None, ge=0, le=100)


class DiagnosticCalculateResponse(BaseModel):
    """Schema para respuesta de cálculo de cotización"""
    equipment_info: Dict[str, Any]
    faults: List[str]
    base_cost: int
    complexity_factor: float
    value_factor: float
    final_cost: int
    min_price: int
    max_price: int
    breakdown: List[FaultBreakdown]
    labor_hours: int
    disclaimer: str
