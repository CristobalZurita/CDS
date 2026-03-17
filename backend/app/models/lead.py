"""
Lead model para capturar prospectos del cotizador público (NOT-clientes).
"""

from sqlalchemy import Column, DateTime, Integer, JSON, String
from sqlalchemy.sql import func

from app.core.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    telefono = Column(String(50), nullable=True)

    # Equipo cotizado
    equipment_brand = Column(String(255), nullable=True)   # nombre de la marca
    equipment_model = Column(String(255), nullable=True)   # nombre del modelo
    equipment_photo_url = Column(String(512), nullable=True)  # si eligió "Otro"

    # Resultado del flujo canónico público (/quotations/estimate)
    quote_result = Column(JSON, nullable=True)  # {final_cost, base_cost, faults, ...}

    # Metadatos
    source = Column(String(50), default="cotizador", nullable=False)
    status = Column(String(50), default="new", nullable=False)  # new, contacted, converted
    ip_address = Column(String(64), nullable=True)
    user_agent = Column(String(512), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<Lead id={self.id} email={self.email} status={self.status}>"
