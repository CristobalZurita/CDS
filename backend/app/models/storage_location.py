"""
Modelo StorageLocation - Ubicaciones de almacenamiento
Alineado con schema real de cirujano.db
"""
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class StorageLocation(Base):
    """Ubicación de almacenamiento para stock y herramientas"""

    __tablename__ = "storage_locations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    location_type = Column(String, nullable=True)
    description = Column(Text, nullable=True)

    # Relaciones
    stocks = relationship("Stock", backref="location")
    tools = relationship("Tool", backref="location")

    def __repr__(self):
        return f"<StorageLocation(id={self.id}, code={self.code})>"
