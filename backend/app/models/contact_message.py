"""
ContactMessage model for storing inbound contact form submissions.
"""

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func
from app.core.database import Base


class ContactMessage(Base):
    __tablename__ = "contact_messages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    subject = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    source_url = Column(String(512), nullable=True)
    ip_address = Column(String(64), nullable=True)
    user_agent = Column(String(512), nullable=True)
    status = Column(String(50), default="new", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<ContactMessage id={self.id} email={self.email}>"
