import threading
import time
import importlib

from fastapi.testclient import TestClient

import backend.app.main as _main
from backend.app.core.database import SessionLocal

importlib.reload(_main)
client = TestClient(_main.app)


def _create_payment(payload, results, index):
    r = client.post("/api/v1/payments/", json=payload)
    results[index] = r


def test_concurrent_duplicate_requests_return_same_payment():
    # Prepare user and repair
    db = SessionLocal()
    try:
        from backend.app.models.user import User
        db_user = db.query(User).filter(User.email == "concurrency@example.com").first()
        if not db_user:
            db_user = User(email="concurrency@example.com", username="concurrency", full_name="Concurrency Test", hashed_password="hashed", role="client", is_active=True)
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
        user_id = db_user.id
    finally:
        db.close()

    res = client.post("/api/v1/repairs/", json={"client_id": user_id, "title": "Concurrency repair", "description": "test"})
    assert res.status_code in (200, 201)
    repair = res.json()
    rid = repair["id"] if isinstance(repair, dict) and "id" in repair else repair[0]["id"]

    tx = "tx_concurrent_123"
    payload = {"repair_id": rid, "amount": 1000, "payment_method": "card", "transaction_id": tx, "user_id": user_id, "status": "success"}

    threads = []
    results = [None] * 5
    for i in range(5):
        t = threading.Thread(target=_create_payment, args=(payload, results, i))
        threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    ids = []
    for r in results:
        assert r is not None
        assert r.status_code in (200, 201)
        body = r.json()
        ids.append(body["id"] if isinstance(body, dict) and "id" in body else body[0]["id"])

    # All returned id values should be the same
    assert len(set(ids)) == 1
