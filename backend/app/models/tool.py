"""
Modelo Tool - Herramientas del taller
Alineado con schema real de cirujano.db
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, Date
from datetime import datetime
from app.core.database import Base


class Tool(Base):
    """Herramienta del taller"""

    __tablename__ = "tools"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, unique=True, nullable=True)
    name = Column(String, nullable=False)
    model = Column(String, nullable=True)
    brand_id = Column(Integer, ForeignKey("tool_brands.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("tool_categories.id"), nullable=True)
    location_id = Column(Integer, ForeignKey("storage_locations.id"), nullable=True)
    serial_number = Column(String, nullable=True)
    specifications = Column(Text, nullable=True)
    status = Column(String, default="available")
    requires_calibration = Column(Integer, default=0)
    last_calibration_date = Column(Date, nullable=True)
    next_calibration_date = Column(Date, nullable=True)
    purchase_price = Column(Float, nullable=True)
    purchase_date = Column(Date, nullable=True)
    warranty_until = Column(Date, nullable=True)
    image_url = Column(Text, nullable=True)
    manual_url = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Tool(id={self.id}, name={self.name}, status={self.status})>"
