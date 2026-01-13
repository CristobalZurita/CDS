"""
Modelo Quote para cotizaciones
"""
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from backend.app.core.database import Base


class QuoteStatus(str, enum.Enum):
    """Estados de cotización"""
    PENDING = "pending"
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


class Quote(Base):
    """
    Modelo para cotizaciones formales
    """

    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True)
    diagnostic_id = Column(Integer, ForeignKey("diagnostics.id"), nullable=True)
    repair_id = Column(Integer, ForeignKey("repairs.id"), nullable=True)

    # Información del instrumento
    instrument_brand = Column(String(100), nullable=False)
    instrument_model = Column(String(100), nullable=False)
    instrument_value = Column(Integer, nullable=True)  # en centavos

    # Items de la cotización
    items = Column(JSON, nullable=True)  # Lista de items con type, description, price

    # Costos
    subtotal = Column(Integer, nullable=False)  # en centavos
    labor_hours = Column(Integer, nullable=True)
    labor_cost = Column(Integer, nullable=True)  # en centavos
    total = Column(Integer, nullable=False)  # en centavos
    min_price = Column(Integer, nullable=True)  # rango mínimo en centavos
    max_price = Column(Integer, nullable=True)  # rango máximo en centavos

    # Estado y validez
    status = Column(Enum(QuoteStatus), default=QuoteStatus.PENDING, nullable=False)
    validity_days = Column(Integer, default=30, nullable=False)

    # Metadatos
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    notes = Column(Text, nullable=True)
    disclaimer = Column(Text, nullable=True)

    # Relaciones
    diagnostic = relationship("Diagnostic", foreign_keys=[diagnostic_id])
    repair = relationship("Repair", foreign_keys=[repair_id])

    def __repr__(self):
        return f"<Quote(id={self.id}, total={self.total}, status={self.status})>"
