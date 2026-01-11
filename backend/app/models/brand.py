"""
Modelo Brand para marcas de instrumentos
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.core.database import Base


class Brand(Base):
    """Marca de instrumentos musicales"""
    
    __tablename__ = "brands"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    country = Column(String(100), nullable=True)
    founded = Column(Integer, nullable=True)  # Año de fundación
    description = Column(Text, nullable=True)
    tier = Column(String(50), nullable=True)  # "budget", "mid-range", "premium", "luxury"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relaciones
    instruments = relationship("Instrument", back_populates="brand")
    
    def __repr__(self):
        return f"<Brand(id={self.id}, name={self.name})>"
