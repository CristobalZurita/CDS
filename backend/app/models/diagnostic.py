"""
Modelo Diagnostic para cotizaciones y análisis IA
"""
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.core.database import Base


class Diagnostic(Base):
    """
    Modelo para almacenar diagnósticos (análisis IA, cotizaciones)
    """
    
    __tablename__ = "diagnostics"
    
    id = Column(Integer, primary_key=True, index=True)
    repair_id = Column(Integer, ForeignKey("repairs.id"), nullable=True)
    
    # Imagen analizada
    image_path = Column(String(500), nullable=True)
    
    # Resultados del análisis IA
    ai_analysis = Column(JSON, nullable=True)  # Resultado de Claude Vision
    detected_faults = Column(JSON, nullable=True)  # [{"fault": "...", "severity": 0-100}]
    ai_confidence = Column(Integer, default=0)  # 0-100
    
    # Cotización generada
    quote_total = Column(Integer, nullable=True)  # en centavos
    quote_breakdown = Column(JSON, nullable=True)  # Desglose por items
    labor_hours = Column(Integer, nullable=True)  # Horas de trabajo estimadas
    
    # Metadatos
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    notes = Column(Text, nullable=True)
    
    # Relaciones
    repair = relationship("Repair", back_populates="diagnostic", foreign_keys=[repair_id], uselist=False)
    
    def __repr__(self):
        return f"<Diagnostic(id={self.id}, ai_confidence={self.ai_confidence})>"
