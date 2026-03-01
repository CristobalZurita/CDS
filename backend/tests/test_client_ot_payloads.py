import importlib

from fastapi.testclient import TestClient

import app.main as _main
from app.core.database import SessionLocal
from app.models.client import Client
from app.models.user import User
from app.routers.client import list_client_purchase_requests
from app.routers.purchase_requests import (
    create_purchase_request,
    list_purchase_requests_board,
    request_client_payment,
)
from app.schemas.purchase_request import PurchaseRequestCreate, PurchaseRequestItemCreate


importlib.reload(_main)


def _build_client() -> TestClient:
    importlib.reload(_main)
    return TestClient(_main.app)


def _ensure_admin_user(user_email: str = "ot-admin@example.com") -> int:
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.id == 1).first()
        if not admin:
            admin = User(
                id=1,
                email=user_email,
                username="otadmin",
                hashed_password="hashed",
                role_id=1,
                is_active=1,
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
        elif admin.role_id != 1:
            admin.role_id = 1
            db.commit()
        return int(admin.id)
    finally:
        db.close()


def _get_admin_client_id() -> int:
    db = SessionLocal()
    try:
        row = db.query(Client).filter(Client.user_id == 1).first()
        if not row:
            row = Client(user_id=1, name="Admin", email="ot-admin@example.com")
            db.add(row)
            db.commit()
            db.refresh(row)
        return int(row.id)
    finally:
        db.close()


def _create_grouped_repairs(client: TestClient) -> tuple[int, int]:
    admin_client_id = _get_admin_client_id()
    base_res = client.post(
        "/api/v1/repairs/",
        json={"client_id": admin_client_id, "title": "OT base", "description": "Base OT"},
    )
    assert base_res.status_code in (200, 201)
    base_id = int(base_res.json()["id"])

    child_res = client.post(
        "/api/v1/repairs/",
        json={
            "client_id": admin_client_id,
            "title": "OT child",
            "description": "Child OT",
            "ot_parent_id": base_id,
        },
    )
    assert child_res.status_code in (200, 201)
    child_id = int(child_res.json()["id"])
    return base_id, child_id


def test_client_repair_payloads_include_repair_code():
    _ensure_admin_user()
    with _build_client() as client:
        _, child_id = _create_grouped_repairs(client)

        list_res = client.get("/api/v1/client/repairs")
        assert list_res.status_code == 200
        rows = list_res.json()
        current = next((item for item in rows if int(item.get("id")) == child_id), None)
        assert current is not None
        assert current.get("repair_code")

        timeline_res = client.get(f"/api/v1/client/repairs/{child_id}/timeline")
        assert timeline_res.status_code == 200
        assert timeline_res.json().get("repair_code")

        detail_res = client.get(f"/api/v1/client/repairs/{child_id}/details")
        assert detail_res.status_code == 200
        detail = detail_res.json()
        assert detail.get("repair", {}).get("repair_code")


def test_purchase_request_payloads_include_repair_code():
    _ensure_admin_user()
    with _build_client() as client:
        admin_client_id = _get_admin_client_id()
        _, child_id = _create_grouped_repairs(client)

    db = SessionLocal()
    try:
        created = create_purchase_request(
            PurchaseRequestCreate(
                client_id=admin_client_id,
                repair_id=child_id,
                notes="Compra OT test",
                items=[
                    PurchaseRequestItemCreate(
                        sku="OT-PR-CODE-001",
                        name="Capacitor test",
                        quantity=1,
                        unit_price=1500,
                    )
                ],
            ),
            db,
            {"user_id": "1", "role": "admin"},
        )
        request_id = int(created.id)

        request_client_payment(
            request_id,
            {"amount": 1500, "due_days": 3},
            db,
            {"user_id": "1", "role": "admin"},
        )

        board_rows = list_purchase_requests_board(None, None, None, db, {"user_id": "1", "role": "admin"}).get("requests", [])
        board_req = next((item for item in board_rows if int(item.get("id")) == request_id), None)
        assert board_req is not None
        assert board_req.get("repair_code")

        client_rows = list_client_purchase_requests(db, {"user_id": "1", "role": "admin"})
        client_req = next((item for item in client_rows if int(item.get("id")) == request_id), None)
        assert client_req is not None
        assert client_req.get("repair_code")
    finally:
        db.close()
