"""Schemas for Diagnostic."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class DiagnosticBase(BaseModel):
    repair_id: Optional[int] = None
    image_path: Optional[str] = None
    ai_analysis: Optional[Dict[str, Any]] = None
    detected_faults: Optional[List[Dict[str, Any]]] = None
    ai_confidence: int = Field(0, ge=0, le=100)
    quote_total: Optional[int] = None
    quote_breakdown: Optional[Dict[str, Any]] = None
    labor_hours: Optional[int] = None
    notes: Optional[str] = None


class DiagnosticCreate(DiagnosticBase):
    pass


class DiagnosticUpdate(BaseModel):
    image_path: Optional[str] = None
    ai_analysis: Optional[Dict[str, Any]] = None
    detected_faults: Optional[List[Dict[str, Any]]] = None
    ai_confidence: Optional[int] = Field(None, ge=0, le=100)
    quote_total: Optional[int] = None
    quote_breakdown: Optional[Dict[str, Any]] = None
    labor_hours: Optional[int] = None
    notes: Optional[str] = None


class DiagnosticRead(DiagnosticBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
