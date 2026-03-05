"""
Modelo Instrument para instrumentos musicales (sintetizadores, etc.)
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


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
    photo_base_url = Column(String(512), nullable=True)
    template_json = Column(JSON, nullable=True)
    mapping_status = Column(String(50), nullable=True)  # pending_map|mapped|verified
    family = Column(String(50), nullable=True)  # 49|61|76|88|module|other
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relaciones
    brand = relationship("Brand", back_populates="instruments")
    photos = relationship("InstrumentPhoto", back_populates="instrument")
    
    def __repr__(self):
        return f"<Instrument(id={self.id}, model={self.model})>"
