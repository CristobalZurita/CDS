"""
Modelo RepairPhoto - Fotos asociadas a reparación
Alineado con schema real de cirujano.db
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class RepairPhoto(Base):
    """Foto asociada a una reparación"""

    __tablename__ = "repair_photos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    repair_id = Column(Integer, ForeignKey("repairs.id"), nullable=False, index=True)
    photo_url = Column(Text, nullable=False)
    photo_type = Column(String, default="general")  # intake, diagnosis, repair, delivery
    caption = Column(Text, nullable=True)
    sort_order = Column(Integer, default=0)
    visible_to_client = Column(Integer, default=1)  # SQLite uses INTEGER for boolean
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    repair = relationship("Repair", back_populates="photos")

    def __repr__(self):
        return f"<RepairPhoto(id={self.id}, repair={self.repair_id}, type={self.photo_type})>"
