import logging
from typing import Optional, Dict, Any
from backend.app.core.database import SessionLocal
from backend.app.models.audit import AuditLog
from backend.app.core.database import engine, Base
from contextlib import contextmanager

logger = logging.getLogger("audit")

@contextmanager
def _get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_audit(event_type: str, user_id: Optional[int] = None, ip_address: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None, message: Optional[str] = None) -> AuditLog:
    """Create an audit log in DB and emit a structured log."""
    try:
        with _get_session() as db:
            record = AuditLog(
                event_type=event_type,
                user_id=user_id,
                ip_address=ip_address,
                details=details,
                message=message,
            )
            db.add(record)
            try:
                db.commit()
                db.refresh(record)
            except Exception as e:
                # Insert failed (DB schema may be missing or DB unreachable).
                # Rollback and fall back to emitting structured log for observability.
                logger.warning("Audit insert failed; rolling back and falling back to structured log: %s", e)
                try:
                    db.rollback()
                except Exception:
                    logger.exception("Rollback failed while handling audit insert error")
    except Exception as e:
        # If DB unavailable, still emit a structured log for observability
        logger.exception("Failed to persist audit log; falling back to structured log: %s", e)
        record = AuditLog(event_type=event_type, user_id=user_id, ip_address=ip_address, details=details, message=message)

    # Emit structured log
    log_payload = {
        "event_type": event_type,
        "user_id": user_id,
        "ip": ip_address,
        "details": details,
        "message": message,
    }
    logger.info(message or "audit event", extra={"audit": log_payload})
    return record
