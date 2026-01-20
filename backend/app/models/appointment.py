"""
Appointment model for booking system
Manages customer appointment requests and scheduling
"""

from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from datetime import datetime
from enum import Enum


class AppointmentType(str, Enum):
    """Tipos de cita"""
    CONSULTATION = "consultation"    # Consulta general
    QUOTE = "quote"                  # Cotización
    REPAIR_PICKUP = "repair_pickup"  # Recepción de equipo
    REPAIR_DELIVERY = "repair_delivery"  # Entrega de equipo
    WARRANTY_CHECK = "warranty_check"  # Revisión de garantía
    MAINTENANCE = "maintenance"      # Mantenimiento preventivo


class Appointment(Base):
    """
    Appointment model for storing customer booking requests
    """
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    telefono = Column(String(20), nullable=False)
    fecha = Column(DateTime, nullable=False, index=True)
    mensaje = Column(Text, nullable=True)
    estado = Column(String(50), default="pendiente", index=True)  # pendiente, confirmado, cancelado
    google_calendar_id = Column(String(255), nullable=True)  # ID del evento en Google Calendar
    notificacion_enviada = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # === CAMPOS ADICIONALES (ADITIVOS) ===
    # Referencias
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=True)
    repair_id = Column(Integer, ForeignKey("repairs.id"), nullable=True)
    technician_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Tipo y duración
    appointment_type = Column(String(30), default=AppointmentType.CONSULTATION.value)
    duration_minutes = Column(Integer, default=30)
    fecha_fin = Column(DateTime, nullable=True)  # Hora de fin calculada

    # Recordatorios
    reminder_sent_at = Column(DateTime, nullable=True)
    reminder_count = Column(Integer, default=0)

    # Cancelación/Reprogramación
    cancellation_reason = Column(Text, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    reschedule_count = Column(Integer, default=0)
    original_fecha = Column(DateTime, nullable=True)  # Fecha original si fue reprogramada

    # Información adicional
    notes_internal = Column(Text, nullable=True)  # Notas solo para staff
    video_call_link = Column(String(500), nullable=True)  # Para consultas remotas
    location = Column(String(255), nullable=True)  # Ubicación si aplica

    # Historial de estados (JSON)
    status_history = Column(Text, nullable=True)  # JSON log de cambios de estado

    # Relaciones (ADITIVAS)
    client = relationship("Client", foreign_keys=[client_id])
    device = relationship("Device", foreign_keys=[device_id])
    repair = relationship("Repair", foreign_keys=[repair_id])
    technician = relationship("User", foreign_keys=[technician_id])

    def __init__(self, **kwargs):
        if "estado" not in kwargs or kwargs.get("estado") is None:
            kwargs["estado"] = "pendiente"
        if "notificacion_enviada" not in kwargs or kwargs.get("notificacion_enviada") is None:
            kwargs["notificacion_enviada"] = False
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Appointment(id={self.id}, nombre={self.nombre}, email={self.email}, fecha={self.fecha})>"

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "email": self.email,
            "telefono": self.telefono,
            "fecha": self.fecha.isoformat() if self.fecha else None,
            "mensaje": self.mensaje,
            "estado": self.estado,
            "google_calendar_id": self.google_calendar_id,
            "notificacion_enviada": self.notificacion_enviada,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
