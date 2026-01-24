"""
PhotoUploadRequest model for token-based client photo upload.
ADITIVO: new table.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class PhotoUploadRequest(Base):
    __tablename__ = "photo_upload_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    repair_id = Column(Integer, ForeignKey("repairs.id"), nullable=False, index=True)
    token = Column(String(255), unique=True, nullable=False, index=True)
    status = Column(String(20), default="pending")  # pending | uploaded | cancelled | expired
    photo_type = Column(String(30), nullable=True)
    caption = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

    repair = relationship("Repair")
