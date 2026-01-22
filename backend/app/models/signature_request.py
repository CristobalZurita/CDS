"""
SignatureRequest model for OT signature flow (ingreso/retiro).
ADITIVO: new table.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class SignatureRequest(Base):
    __tablename__ = "signature_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    repair_id = Column(Integer, ForeignKey("repairs.id"), nullable=False, index=True)
    request_type = Column(String(20), nullable=False)  # ingreso | retiro
    token = Column(String(255), unique=True, nullable=False, index=True)
    status = Column(String(20), default="pending")  # pending | signed | cancelled | expired
    created_at = Column(DateTime, default=datetime.utcnow)
    signed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)

    # Optional metadata
    signed_ip = Column(String(64), nullable=True)
    signed_user_agent = Column(String(255), nullable=True)

    repair = relationship("Repair", back_populates="signature_requests")
