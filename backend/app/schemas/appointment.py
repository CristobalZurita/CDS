"""
Pydantic schemas for Appointment API
Request/Response validation and serialization
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import re


class AppointmentCreate(BaseModel):
    """Schema for creating a new appointment"""
    nombre: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    telefono: str = Field(..., min_length=10, max_length=20)
    fecha: datetime
    mensaje: Optional[str] = Field(None, max_length=1000)

    @validator('nombre')
    def validate_nombre(cls, v):
        """Validate that nombre contains only letters, accents, and Ñ"""
        # Allow letters, accents, spaces, and Ñ
        if not re.match(r"^[a-záéíóúñA-ZÁÉÍÓÚÑ\s]+$", v):
            raise ValueError('El nombre solo puede contener letras, acentos y espacios')
        return v.strip()

    @validator('telefono')
    def validate_telefono(cls, v):
        """Validate that telefono starts with + and contains only numbers"""
        if not re.match(r"^\+\d+$", v):
            raise ValueError('El teléfono debe comenzar con + y solo contener números')
        return v.strip()

    @validator('fecha')
    def validate_fecha(cls, v):
        """Validate that fecha is in the future"""
        if v <= datetime.now():
            raise ValueError('La fecha debe ser en el futuro')
        return v

    @validator('mensaje')
    def validate_mensaje(cls, v):
        """Clean up mensaje if provided"""
        if v:
            return v.strip()
        return v

    class Config:
        schema_extra = {
            "example": {
                "nombre": "Juan García Pérez",
                "email": "juan@ejemplo.com",
                "telefono": "+56912345678",
                "fecha": "2024-12-20T14:30:00",
                "mensaje": "Consulta sobre reparación de sintetizador"
            }
        }


class AppointmentUpdate(BaseModel):
    """Schema for updating an appointment"""
    estado: Optional[str] = None
    google_calendar_id: Optional[str] = None
    notificacion_enviada: Optional[bool] = None

    class Config:
        schema_extra = {
            "example": {
                "estado": "confirmado",
                "google_calendar_id": "abc123def456",
                "notificacion_enviada": True
            }
        }


class AppointmentResponse(BaseModel):
    """Schema for appointment response"""
    id: int
    nombre: str
    email: str
    telefono: str
    fecha: datetime
    mensaje: Optional[str]
    estado: str
    google_calendar_id: Optional[str]
    notificacion_enviada: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "nombre": "Juan García Pérez",
                "email": "juan@ejemplo.com",
                "telefono": "+56912345678",
                "fecha": "2024-12-20T14:30:00",
                "mensaje": "Consulta sobre reparación",
                "estado": "pendiente",
                "google_calendar_id": None,
                "notificacion_enviada": False,
                "created_at": "2024-12-15T10:00:00",
                "updated_at": None
            }
        }
