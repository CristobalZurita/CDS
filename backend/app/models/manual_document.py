"""
ManualDocument model to link manuals/diagrams with instruments.
ADITIVO: new table.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class ManualDocument(Base):
    __tablename__ = "manual_documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    instrument_id = Column(Integer, ForeignKey("instruments.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    source = Column(String(50), default="internal")  # internal | external
    url = Column(String(500), nullable=True)
    file_path = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    instrument = relationship("Instrument")
