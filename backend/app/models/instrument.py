"""
Modelo Instrument para instrumentos musicales (sintetizadores, etc.)
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.core.database import Base


class Instrument(Base):
    """Modelo de instrumento musical en el catálogo"""
    
    __tablename__ = "instruments"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=True)
    
    # Información básica
    name = Column(String(255), nullable=False, index=True)
    model = Column(String(255), nullable=False, index=True)
    type = Column(String(100), nullable=True)  # "synthesizer", "keyboard", "drum_machine", etc.
    year = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    
    # Estimación de precio (para cotización automática)
    valor_estimado = Column(Integer, nullable=True)  # Valor estimado en centavos
    
    # Imagen
    image = Column(JSON, nullable=True)  # {"url": "...", "status": "pending|loaded|failed"}
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relaciones
    brand = relationship("Brand", back_populates="instruments")
    repairs = relationship("Repair", back_populates="instrument")
    
    def __repr__(self):
        return f"<Instrument(id={self.id}, model={self.model})>"
