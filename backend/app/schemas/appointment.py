"""
Pydantic schemas for Appointment API
Request/Response validation and serialization
"""

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
import re

from app.core.timezone import now_utc, to_local, to_utc


def _build_allowed_appointment_slots() -> set[str]:
    slots = []
    for hour in (9, 10, 11):
        for minute in (0, 30):
            slots.append(f"{hour:02d}:{minute:02d}")
    for hour in (14, 15, 16, 17):
        for minute in (0, 30):
            slots.append(f"{hour:02d}:{minute:02d}")
    return set(slots)


ALLOWED_APPOINTMENT_SLOTS = _build_allowed_appointment_slots()


class AppointmentCreate(BaseModel):
    """Schema for creating a new appointment"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "Juan García Pérez",
                "email": "juan@ejemplo.com",
                "telefono": "+56912345678",
                "fecha": "2024-12-20T14:30:00",
                "mensaje": "Consulta sobre reparación de sintetizador"
            }
        }
    )

    nombre: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    telefono: str = Field(..., min_length=10, max_length=20)
    fecha: datetime
    mensaje: Optional[str] = Field(None, max_length=1000)
    turnstile_token: Optional[str] = None

    @field_validator('nombre')
    @classmethod
    def validate_nombre(cls, v):
        """Validate that nombre contains only letters, accents, and Ñ"""
        # Allow letters, accents, spaces, and Ñ
        if not re.match(r"^[a-záéíóúñA-ZÁÉÍÓÚÑ\s]+$", v):
            raise ValueError('El nombre solo puede contener letras, acentos y espacios')
        return v.strip()

    @field_validator('telefono')
    @classmethod
    def validate_telefono(cls, v):
        """Validate that telefono starts with + and contains only numbers"""
        if not re.match(r"^\+\d+$", v):
            raise ValueError('El teléfono debe comenzar con + y solo contener números')
        return v.strip()

    @field_validator('fecha')
    @classmethod
    def validate_fecha(cls, v):
        """Validate that fecha is in the future"""
        normalized = to_utc(v)
        if normalized <= now_utc():
            raise ValueError('La fecha debe ser en el futuro')
        local_datetime = to_local(normalized)
        if local_datetime.weekday() >= 5:
            raise ValueError('Solo se permiten citas de lunes a viernes')

        slot = local_datetime.strftime("%H:%M")
        if slot not in ALLOWED_APPOINTMENT_SLOTS:
            raise ValueError('La hora debe coincidir con un bloque disponible del calendario')
        return normalized

    @field_validator('mensaje')
    @classmethod
    def validate_mensaje(cls, v):
        """Clean up mensaje if provided"""
        if v:
            return v.strip()
        return v


class AppointmentUpdate(BaseModel):
    """Schema for updating an appointment"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "estado": "confirmado",
                "google_calendar_id": "abc123def456",
                "notificacion_enviada": True
            }
        }
    )

    estado: Optional[str] = None
    fecha: Optional[datetime] = None
    mensaje: Optional[str] = Field(None, max_length=1000)
    cancellation_reason: Optional[str] = Field(None, max_length=1000)
    google_calendar_id: Optional[str] = None
    notificacion_enviada: Optional[bool] = None

    @field_validator('fecha')
    @classmethod
    def validate_fecha(cls, v):
        if v is None:
            return v
        normalized = to_utc(v)
        if normalized <= now_utc():
            raise ValueError('La fecha debe ser en el futuro')
        local_datetime = to_local(normalized)
        if local_datetime.weekday() >= 5:
            raise ValueError('Solo se permiten citas de lunes a viernes')

        slot = local_datetime.strftime("%H:%M")
        if slot not in ALLOWED_APPOINTMENT_SLOTS:
            raise ValueError('La hora debe coincidir con un bloque disponible del calendario')
        return normalized

    @field_validator('mensaje', 'cancellation_reason')
    @classmethod
    def validate_optional_text(cls, value):
        if value:
            return value.strip()
        return value


class AppointmentResponse(BaseModel):
    """Schema for appointment response"""
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
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
    )

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
