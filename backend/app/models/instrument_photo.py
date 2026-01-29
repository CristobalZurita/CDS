"""
Fotos asociadas a instrumentos (base/cliente/técnico).
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class InstrumentPhoto(Base):
    __tablename__ = "instrument_photos"

    id = Column(Integer, primary_key=True, index=True)
    instrument_id = Column(Integer, ForeignKey("instruments.id"), nullable=False, index=True)
    role = Column(String(50), nullable=False)  # base|cliente|tecnico
    url = Column(String(512), nullable=False)
    meta = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    instrument = relationship("Instrument", back_populates="photos")

    def __repr__(self):
        return f"<InstrumentPhoto(id={self.id}, role={self.role})>"
