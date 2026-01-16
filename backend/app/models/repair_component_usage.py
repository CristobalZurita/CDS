"""
Modelo RepairComponentUsage - Registro de componentes usados en reparación
Alineado con schema real de cirujano.db
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class RepairComponentUsage(Base):
    """Registro de uso de componente en una reparación"""

    __tablename__ = "repair_component_usage"

    id = Column(Integer, primary_key=True, autoincrement=True)
    repair_id = Column(Integer, ForeignKey("repairs.id"), nullable=False, index=True)
    component_table = Column(String, nullable=False)
    component_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_cost = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    repair = relationship("Repair", back_populates="component_usages")

    @property
    def total_cost(self):
        """Costo total = cantidad * costo unitario"""
        if self.unit_cost:
            return self.quantity * self.unit_cost
        return 0.0

    def __repr__(self):
        return f"<RepairComponentUsage(repair={self.repair_id}, table={self.component_table}, qty={self.quantity})>"
