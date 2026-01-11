from backend.app.services.logging_service import create_audit
from backend.app.core.database import SessionLocal
from backend.app.models.audit import AuditLog


def test_create_audit_record():
    # Create an audit record and verify it is stored in DB
    rec = create_audit(event_type="test.event", user_id=123, ip_address="127.0.0.1", details={"k":"v"}, message="Test audit")
    assert isinstance(rec, AuditLog)
    # Query the DB to ensure record exists
    db = SessionLocal()
    try:
        q = db.query(AuditLog).filter(AuditLog.id == rec.id).first()
        assert q is not None
        assert q.event_type == "test.event"
        assert q.user_id == 123
    finally:
        db.close()
