"""
Appointment model for booking system
Manages customer appointment requests and scheduling
"""

from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean
from sqlalchemy.sql import func
from backend.app.core.database import Base
from datetime import datetime


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
