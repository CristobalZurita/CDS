"""
Modelo StockMovement para historial de movimientos de inventario
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from backend.app.core.database import Base


class MovementType(str, enum.Enum):
    """Tipos de movimientos de inventario"""
    ENTRY = "entry"           # Entrada de stock
    WITHDRAWAL = "withdrawal" # Salida de stock
    ADJUSTMENT = "adjustment" # Ajuste de inventario
    DAMAGE = "damage"         # Producto dañado


class StockMovement(Base):
    """Registro de movimiento de stock"""
    
    __tablename__ = "stock_movements"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    
    # Información del movimiento
    movement_type = Column(Enum(MovementType), nullable=False)
    quantity = Column(Integer, nullable=False)
    reason = Column(String(255), nullable=True)  # Motivo del movimiento
    notes = Column(Text, nullable=True)
    
    # Fecha
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    product = relationship("Product", back_populates="stock_movements")
    
    def __repr__(self):
        return f"<StockMovement(id={self.id}, type={self.movement_type}, qty={self.quantity})>"
