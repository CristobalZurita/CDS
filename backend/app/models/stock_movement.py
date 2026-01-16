"""
Modelo StockMovement para historial de movimientos de inventario
Alineado con schema real de cirujano.db
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class StockMovement(Base):
    """
    Registro de movimiento de stock.
    Refleja exactamente la tabla stock_movements de cirujano.db.
    """

    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_id = Column(Integer, ForeignKey("stock.id"), nullable=False, index=True)
    movement_type = Column(String, nullable=False)  # DB usa TEXT, no Enum
    quantity = Column(Integer, nullable=False)
    repair_id = Column(Integer, ForeignKey("repairs.id"), nullable=True)
    notes = Column(Text, nullable=True)
    performed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    stock = relationship("Stock", back_populates="movements")
    repair = relationship("Repair", foreign_keys=[repair_id])
    user = relationship("User", foreign_keys=[performed_by])

    def __repr__(self):
        return f"<StockMovement(id={self.id}, type={self.movement_type}, qty={self.quantity})>"
