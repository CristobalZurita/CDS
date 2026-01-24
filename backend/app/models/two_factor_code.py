"""
TwoFactorCode model for email-based 2FA.
ADITIVO: new table.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class TwoFactorCode(Base):
    __tablename__ = "two_factor_codes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    code = Column(String(10), nullable=False)
    status = Column(String(20), default="active")  # active | used | expired
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

    user = relationship("User")
