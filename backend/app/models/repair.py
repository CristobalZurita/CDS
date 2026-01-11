"""
Modelo Repair para gestionar reparaciones
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from backend.app.core.database import Base


class RepairStatus(str, enum.Enum):
    """Estados posibles de una reparación"""
    PENDING = "pending"           # Pendiente de revisión
    IN_PROGRESS = "in_progress"   # En reparación
    WAITING_PARTS = "waiting_parts"  # Esperando repuestos
    COMPLETED = "completed"       # Reparación completada
    READY_PICKUP = "ready_pickup" # Listo para recoger
    DELIVERED = "delivered"       # Entregado
    CANCELLED = "cancelled"       # Cancelado


class Repair(Base):
    """Modelo de reparación"""
    
    __tablename__ = "repairs"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    instrument_id = Column(Integer, ForeignKey("instruments.id"), nullable=True)
    # diagnostic_id removed to avoid circular FK ambiguity; Diagnostic.repair_id references Repair.id
    
    # Información general
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(RepairStatus), default=RepairStatus.PENDING, nullable=False)
    
    # Estimados
    estimated_price = Column(Integer, nullable=True)  # en centavos
    final_price = Column(Integer, nullable=True)
    estimated_days = Column(Integer, nullable=True)
    
    # Fechas
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Control
    notes = Column(Text, nullable=True)
    is_priority = Column(Boolean, default=False)
    
    # Relaciones
    client = relationship("User", back_populates="repairs", foreign_keys=[client_id])
    instrument = relationship("Instrument", back_populates="repairs")
    diagnostic = relationship("Diagnostic", back_populates="repair", uselist=False)
    
    def __repr__(self):
        return f"<Repair(id={self.id}, client_id={self.client_id}, status={self.status})>"
