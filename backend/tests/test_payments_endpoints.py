from fastapi.testclient import TestClient
import importlib
import backend.app.main as _main
from backend.app.core.database import SessionLocal
from backend.app.models.payment import Payment

importlib.reload(_main)
client = TestClient(_main.app)


def _count_payments_with_tx(tx: str):
    db = SessionLocal()
    try:
        return db.query(Payment).filter(Payment.transaction_id == tx).count()
    finally:
        db.close()


def test_payment_idempotency():
    importlib.reload(_main)
    client = TestClient(_main.app)

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

    # create repair
    res = client.post("/api/v1/repairs/", json={"client_id": user_id, "title": "Idempotency repair", "description": "testing"})
    assert res.status_code in (200, 201)
    repair = res.json()
    rid = repair["id"] if isinstance(repair, dict) and "id" in repair else repair[0]["id"]

    tx = "txdup123"
    payload = {"repair_id": rid, "amount": 1000, "payment_method": "card", "transaction_id": tx, "user_id": user_id, "status": "success"}
    r1 = client.post("/api/v1/payments/", json=payload)
    assert r1.status_code in (200, 201)
    p1 = r1.json()
    assert "id" in p1

    r2 = client.post("/api/v1/payments/", json=payload)
    assert r2.status_code == 200
    p2 = r2.json()
    assert p2["id"] == p1["id"]

    # ensure only one payment exists with that transaction id
    assert _count_payments_with_tx(tx) == 1


def test_get_and_list_payments():
    importlib.reload(_main)
    client = TestClient(_main.app)

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

    # create repair
    res = client.post("/api/v1/repairs/", json={"client_id": user_id, "title": "List repair", "description": "testing list"})
    assert res.status_code in (200, 201)
    repair = res.json()
    rid = repair["id"] if isinstance(repair, dict) and "id" in repair else repair[0]["id"]

    # create two payments (unique transaction ids to avoid test collisions)
    import uuid
    p1 = {"repair_id": rid, "amount": 1100, "payment_method": "cash", "transaction_id": f"tx_{uuid.uuid4().hex[:8]}", "user_id": user_id, "status": "success"}
    p2 = {"repair_id": rid, "amount": 1200, "payment_method": "cash", "transaction_id": f"tx_{uuid.uuid4().hex[:8]}", "user_id": user_id, "status": "success"}
    r1 = client.post("/api/v1/payments/", json=p1)
    r2 = client.post("/api/v1/payments/", json=p2)
    assert r1.status_code in (200, 201)
    assert r2.status_code in (200, 201)

    # list payments for repair
    res = client.get(f"/api/v1/payments/?repair_id={rid}")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 2

    # get a specific payment
    some = data[0]
    pid = some["id"]
    resp = client.get(f"/api/v1/payments/{pid}")
    assert resp.status_code == 200
    got = resp.json()
    assert got["id"] == pid

    # audit checks for list and get
    from backend.app.models.audit import AuditLog
    db = SessionLocal()
    try:
        last_list = db.query(AuditLog).filter(AuditLog.event_type == "payment.list").order_by(AuditLog.created_at.desc()).first()
        assert last_list is not None
        last_get = db.query(AuditLog).filter(AuditLog.event_type == "payment.get").order_by(AuditLog.created_at.desc()).first()
        assert last_get is not None and last_get.details and last_get.details.get("payment_id") == pid
    finally:
        db.close()


def test_invalid_payment_amount():
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

    # create repair
    res = client.post("/api/v1/repairs/", json={"client_id": user_id, "title": "Bad payment repair", "description": "testing"})
    assert res.status_code in (200, 201)
    repair = res.json()
    rid = repair["id"] if isinstance(repair, dict) and "id" in repair else repair[0]["id"]

    payload = {"repair_id": rid, "amount": 0, "payment_method": "card", "transaction_id": "tx_bad_amount", "user_id": user_id, "status": "success"}
    r = client.post("/api/v1/payments/", json=payload)
    # Pydantic validation should reject amount <= 0 with 422
    assert r.status_code == 422


def test_invalid_payment_method():
    importlib.reload(_main)
    client = TestClient(_main.app)

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

    res = client.post("/api/v1/repairs/", json={"client_id": user_id, "title": "Bad method repair", "description": "testing"})
    assert res.status_code in (200, 201)
    repair = res.json()
    rid = repair["id"] if isinstance(repair, dict) and "id" in repair else repair[0]["id"]

    payload = {"repair_id": rid, "amount": 1000, "payment_method": "cheque", "transaction_id": "tx_bad_method", "user_id": user_id, "status": "success"}
    r = client.post("/api/v1/payments/", json=payload)
    assert r.status_code == 422


def test_duplicate_transaction_returns_existing():
    importlib.reload(_main)
    client = TestClient(_main.app)

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

    res = client.post("/api/v1/repairs/", json={"client_id": user_id, "title": "Dup repair", "description": "testing"})
    assert res.status_code in (200, 201)
    repair = res.json()
    rid = repair["id"] if isinstance(repair, dict) and "id" in repair else repair[0]["id"]

    tx = "tx_existing_db"
    # Create payment directly in DB, simulating a pre-existing payment
    db = SessionLocal()
    try:
        from backend.app.models.payment import Payment, PaymentStatus
        pay = Payment(user_id=user_id, repair_id=rid, amount=999, payment_method="card", transaction_id=tx, status=PaymentStatus.SUCCESS)
        db.add(pay)
        db.commit()
        db.refresh(pay)
        existing_id = pay.id
    finally:
        db.close()

    payload = {"repair_id": rid, "amount": 1500, "payment_method": "card", "transaction_id": tx, "user_id": user_id, "status": "success"}
    r = client.post("/api/v1/payments/", json=payload)
    assert r.status_code == 200
    p = r.json()
    assert p["id"] == existing_id
