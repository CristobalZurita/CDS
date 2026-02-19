"""
Modelo RepairIntakeSheet
========================
Planilla detallada de ingreso OT (operación y mantenimiento), vinculada 1:1 a una reparación.

ADITIVO:
- No reemplaza datos existentes de Repair/Device/Client.
- Agrega trazabilidad estructurada para formulario operativo.
"""

from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class RepairIntakeSheet(Base):
    __tablename__ = "repair_intake_sheets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    repair_id = Column(Integer, ForeignKey("repairs.id"), nullable=False, unique=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Nomenclatura operacional
    client_code = Column(String(32), nullable=True)
    ot_code = Column(String(64), nullable=True)
    instrument_code = Column(String(64), nullable=True)

    # Encabezado de equipo/servicio
    equipment_name = Column(String(255), nullable=True)
    equipment_model = Column(String(255), nullable=True)
    equipment_type = Column(String(30), nullable=True)  # general | precision
    requested_service_type = Column(String(30), nullable=True)  # emergency | maintenance
    downtime_description = Column(Text, nullable=True)
    failure_cause = Column(Text, nullable=True)

    # Costos y planificación
    repair_tariff = Column(Float, nullable=True)
    material_tariff = Column(Float, nullable=True)
    estimated_repair_time = Column(String(120), nullable=True)
    estimated_completion_date = Column(Date, nullable=True)

    # Firmas / aprobaciones por área
    operation_department_signed_by = Column(String(255), nullable=True)
    operation_department_signed_at = Column(Date, nullable=True)
    finance_department_signed_by = Column(String(255), nullable=True)
    finance_department_signed_at = Column(Date, nullable=True)
    factory_director_signed_by = Column(String(255), nullable=True)
    factory_director_signed_at = Column(Date, nullable=True)
    general_manager_signed_by = Column(String(255), nullable=True)
    general_manager_signed_at = Column(Date, nullable=True)

    tabulator_name = Column(String(255), nullable=True)
    form_date = Column(Date, nullable=True)
    annotations = Column(Text, nullable=True)

    # Snapshot payload para auditoría/completitud
    form_payload_json = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    repair = relationship("Repair", back_populates="intake_sheet")
    client = relationship("Client")
    device = relationship("Device")
    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self) -> str:
        return f"<RepairIntakeSheet(id={self.id}, repair_id={self.repair_id}, ot_code={self.ot_code})>"
