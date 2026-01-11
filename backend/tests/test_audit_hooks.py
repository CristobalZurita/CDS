import io
from fastapi.testclient import TestClient
import importlib
import backend.app.main as _main
import backend.app.core.database as _db_core

importlib.reload(_main)
app = _main.app

from backend.app.core.database import SessionLocal
from backend.app.models.audit import AuditLog

client = TestClient(app)


def _latest_audit(event_type: str):
    db = SessionLocal()
    try:
        return db.query(AuditLog).filter(AuditLog.event_type == event_type).order_by(AuditLog.created_at.desc()).first()
    finally:
        db.close()


def test_repair_crud_audit():
    # Ensure app routes are up-to-date after recent router fixes
    importlib.reload(_main)
    client = TestClient(_main.app)
    # Create a user to own the repair
    db = SessionLocal()
    user = None
    try:
        from backend.app.models.user import User
        # Reuse existing test user if present to avoid unique constraint issues
        db_user = db.query(User).filter(User.email == "audit@example.com").first()
        if not db_user:
            db_user = User(email="audit@example.com", username="audittest", full_name="Audit Test", hashed_password="hashed", role="client", is_active=True)
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
        user = db_user.id
    finally:
        db.close()

    # Create repair
    payload = {"client_id": user, "title": "Test repair", "description": "Test audit create"}
    res = client.post("/api/v1/repairs/", json=payload)
    assert res.status_code in (200, 201)
    data = res.json()
    assert "id" in data
    rid = data["id"]

    rec = _latest_audit("repair.create")
    assert rec is not None
    assert rec.details and rec.details.get("repair_id") == rid

    # Update
    upd = {"technical_notes": "updated note"}
    res = client.put(f"/api/v1/repairs/{rid}", json=upd)
    assert res.status_code == 200
    rec = _latest_audit("repair.update")
    assert rec is not None and rec.details.get("repair_id") == rid

    # Delete
    res = client.delete(f"/api/v1/repairs/{rid}")
    assert res.status_code == 200
    rec = _latest_audit("repair.delete")
    assert rec is not None and rec.details.get("repair_id") == rid


def test_upload_image_creates_audit(tmp_path):
    importlib.reload(_main)
    client = TestClient(_main.app)
    img = io.BytesIO()
    img.write(b"\x89PNG\r\n\x1a\n")
    img.seek(0)
    files = {"file": ("audit.png", img, "image/png")}
    res = client.post("/api/v1/uploads/images", files=files)
    assert res.status_code in (200, 201)
    rec = _latest_audit("upload.image")
    assert rec is not None
    assert rec.details and "filename" in rec.details or "path" in rec.details


def test_diagnostic_calculate_creates_audit():
    importlib.reload(_main)
    client = TestClient(_main.app)

    payload = {
        "equipment": {"brand": "access", "model": "access-virus-c-desktop"},
        "faults": ["CONNECTOR_LOOSE"],
    }
    res = client.post("/api/v1/diagnostic/calculate", json=payload)
    assert res.status_code == 200
    rec = _latest_audit("diagnostic.calculate")
    assert rec is not None
    assert rec.details and rec.details.get("model") == "access-virus-c-desktop"


def test_payment_create_emits_audit():
    importlib.reload(_main)
    client = TestClient(_main.app)

    # ensure user exists
    db = SessionLocal()
    try:
        from backend.app.models.user import User
        db_user = db.query(User).filter(User.email == "audit@example.com").first()
        if not db_user:
            db_user = User(email="audit@example.com", username="audittest", full_name="Audit Test", hashed_password="hashed", role="client", is_active=True)
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
        user_id = db_user.id
    finally:
        db.close()

    # create repair via API
    payload = {"client_id": user_id, "title": "Payment test repair", "description": "Payment flow test"}
    res = client.post("/api/v1/repairs/", json=payload)
    assert res.status_code in (200, 201)
    repair = res.json()
    rid = repair["id"] if isinstance(repair, dict) and "id" in repair else repair[0]["id"]

    import uuid
    tx = f"tx_{uuid.uuid4().hex[:8]}"
    pay = {"repair_id": rid, "amount": 5000, "payment_method": "card", "transaction_id": tx, "user_id": user_id, "status": "success"}
    res = client.post("/api/v1/payments/", json=pay)
    assert res.status_code in (200, 201)
    p = res.json()
    assert "id" in p

    rec = _latest_audit("payment.create")
    assert rec is not None
    assert rec.details and rec.details.get("repair_id") == rid
    # ensure audit includes transaction_id and status
    assert "transaction_id" in rec.details and "status" in rec.details
