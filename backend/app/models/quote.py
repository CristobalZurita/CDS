"""
Modelo Quote - Cotizaciones
Alineado con schema real de cirujano.db
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Quote(Base):
    """Cotización de reparación"""

    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    quote_number = Column(String, unique=True, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=True)
    problem_description = Column(Text, nullable=False)
    photos_received = Column(Text, nullable=True)
    diagnosis = Column(Text, nullable=True)
    estimated_hours = Column(Float, nullable=True)
    estimated_parts_cost = Column(Float, default=0)
    estimated_labor_cost = Column(Float, default=0)
    estimated_total = Column(Float, default=0)
    status = Column(String, default="pending")
    valid_until = Column(Date, nullable=True)
    client_response = Column(Text, nullable=True)
    responded_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relaciones
    client = relationship("Client", back_populates="quotes")
    creator = relationship("User", foreign_keys=[created_by])
    repairs = relationship("Repair", backref="quote")

    def __repr__(self):
        return f"<Quote(id={self.id}, number={self.quote_number}, status={self.status})>"
