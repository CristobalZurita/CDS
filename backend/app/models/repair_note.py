"""
Modelo RepairNote - Notas de reparación
Alineado con schema real de cirujano.db
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class RepairNote(Base):
    """Nota asociada a una reparación"""

    __tablename__ = "repair_notes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    repair_id = Column(Integer, ForeignKey("repairs.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    note = Column(Text, nullable=False)
    note_type = Column(String, default="internal")  # internal, client, diagnosis
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    repair = relationship("Repair", back_populates="notes")
    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<RepairNote(id={self.id}, repair={self.repair_id}, type={self.note_type})>"
