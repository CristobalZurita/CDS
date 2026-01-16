"""
Modelo Device - Equipos/dispositivos de clientes
Alineado con schema real de cirujano.db
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Device(Base):
    """Equipo o dispositivo de un cliente para reparación"""

    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    device_type_id = Column(Integer, ForeignKey("device_types.id"), nullable=False)
    brand_id = Column(Integer, ForeignKey("device_brands.id"), nullable=True)
    brand_other = Column(Text, nullable=True)
    model = Column(String, nullable=False)
    serial_number = Column(String, nullable=True)
    year_manufactured = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    condition_notes = Column(Text, nullable=True)
    photos = Column(Text, nullable=True)  # JSON string
    total_repairs = Column(Integer, default=0)
    first_repair_date = Column(Date, nullable=True)
    last_repair_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    client = relationship("Client", back_populates="devices")
    repairs = relationship("Repair", backref="device")
    quotes = relationship("Quote", backref="device")

    def __repr__(self):
        return f"<Device(id={self.id}, model={self.model})>"
