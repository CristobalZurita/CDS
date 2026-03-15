"""
Pydantic schemas para leads del cotizador público.
"""

from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Any, Dict, Optional
from datetime import datetime


class LeadCreate(BaseModel):
    nombre: str
    email: EmailStr
    telefono: Optional[str] = None
    equipment_brand: Optional[str] = None
    equipment_model: Optional[str] = None
    equipment_photo_url: Optional[str] = None
    quote_result: Optional[Dict[str, Any]] = None
    turnstile_token: Optional[str] = None


class LeadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    email: EmailStr
    telefono: Optional[str] = None
    equipment_brand: Optional[str] = None
    equipment_model: Optional[str] = None
    equipment_photo_url: Optional[str] = None
    quote_result: Optional[Dict[str, Any]] = None
    source: str
    status: str
    created_at: datetime
