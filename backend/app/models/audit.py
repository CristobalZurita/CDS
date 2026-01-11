from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, Index
from datetime import datetime
from backend.app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(120), nullable=False, index=True)
    user_id = Column(Integer, nullable=True, index=True)
    ip_address = Column(String(45), nullable=True)
    details = Column(JSON, nullable=True)
    message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


# Optional index on (event_type, created_at) for fast lookups
Index("ix_audit_event_created", AuditLog.event_type, AuditLog.created_at)
