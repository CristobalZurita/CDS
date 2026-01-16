"""
Modelo Repair para gestionar reparaciones - Alineado con schema real de cirujano.db
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class RepairStatus(Base):
    """Modelo de estados de reparación"""
    __tablename__ = "repair_statuses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String, nullable=True)

    repairs = relationship("Repair", back_populates="status_obj")


class Repair(Base):
    """Modelo de reparación - coincide con schema real de cirujano.db"""

    __tablename__ = "repairs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    repair_number = Column(String, unique=True, nullable=False)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True)
    quote_id = Column(Integer, ForeignKey("quotes.id"), nullable=True)
    status_id = Column(Integer, ForeignKey("repair_statuses.id"), nullable=False, default=1, index=True)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Fechas del proceso
    intake_date = Column(DateTime, default=datetime.utcnow)
    diagnosis_date = Column(DateTime, nullable=True)
    approval_date = Column(DateTime, nullable=True)
    start_date = Column(DateTime, nullable=True)
    completion_date = Column(DateTime, nullable=True)
    delivery_date = Column(DateTime, nullable=True)

    # Información de la reparación
    problem_reported = Column(Text, nullable=False)
    diagnosis = Column(Text, nullable=True)
    work_performed = Column(Text, nullable=True)

    # Costos
    parts_cost = Column(Float, default=0)
    labor_cost = Column(Float, default=0)
    additional_cost = Column(Float, default=0)
    discount = Column(Float, default=0)
    total_cost = Column(Float, default=0)

    # Pago
    payment_status = Column(String, default='pending')
    payment_method = Column(String, nullable=True)
    paid_amount = Column(Float, default=0)

    # Garantía
    warranty_days = Column(Integer, default=90)
    warranty_until = Column(Date, nullable=True)

    # Control
    priority = Column(Integer, default=2)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    status_obj = relationship("RepairStatus", back_populates="repairs")
    technician = relationship("User", back_populates="repairs", foreign_keys=[assigned_to])
    diagnostic = relationship("Diagnostic", back_populates="repair", uselist=False)

    @property
    def status(self):
        """Propiedad para compatibilidad - retorna nombre del estado"""
        if self.status_obj:
            return self.status_obj.name
        status_map = {1: "pending", 2: "in_progress", 3: "completed", 4: "delivered"}
        return status_map.get(self.status_id, "pending")

    def __repr__(self):
        return f"<Repair(id={self.id}, repair_number={self.repair_number}, status_id={self.status_id})>"
