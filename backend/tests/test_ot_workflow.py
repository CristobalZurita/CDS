import importlib

from fastapi.testclient import TestClient

import app.main as _main
from app.core.database import SessionLocal
from app.models.category import Category
from app.models.client import Client
from app.models.inventory import Product
from app.models.stock import Stock
from app.models.stock_movement import StockMovement
from app.models.user import User


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


def _create_user(email: str) -> int:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                email=email,
                username=email.split("@")[0],
                hashed_password="hashed",
                role="client",
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        return int(user.id)
    finally:
        db.close()


def _get_client_id_for_user(user_id: int) -> int:
    db = SessionLocal()
    try:
        client = db.query(Client).filter(Client.user_id == user_id).first()
        assert client is not None
        return int(client.id)
    finally:
        db.close()


def test_ot_group_generation_and_next_code():
    _ensure_admin_user()
    client = _build_client()

    user_id = _create_user("ot-user-a@example.com")

    first = client.post(
        "/api/v1/repairs/",
        json={"client_id": user_id, "title": "Base OT", "description": "first"},
    )
    assert first.status_code in (200, 201)
    first_body = first.json()
    first_id = int(first_body["id"])

    client_id = _get_client_id_for_user(user_id)

    preview = client.get(
        "/api/v1/repairs/next-code",
        params={"client_id": client_id, "ot_parent_id": first_id},
    )
    assert preview.status_code == 200
    preview_body = preview.json()
    assert preview_body["ot_parent_id"] == first_id
    assert int(preview_body["next_suffix"]) >= 2

    second = client.post(
        "/api/v1/repairs/",
        json={
            "client_id": user_id,
            "title": "Grouped OT",
            "description": "second",
            "ot_parent_id": first_id,
        },
    )
    assert second.status_code in (200, 201)
    second_id = int(second.json()["id"])

    first_detail = client.get(f"/api/v1/repairs/{first_id}")
    second_detail = client.get(f"/api/v1/repairs/{second_id}")
    assert first_detail.status_code == 200
    assert second_detail.status_code == 200

    first_data = first_detail.json()
    second_data = second_detail.json()

    assert int(first_data["ot_parent_id"]) == first_id
    assert int(first_data["ot_sequence"]) == 1
    assert str(first_data["repair_code"]).endswith("-01")

    assert int(second_data["ot_parent_id"]) == first_id
    assert int(second_data["ot_sequence"]) >= 2
    assert str(second_data["repair_code"]).endswith(f"-{int(second_data['ot_sequence']):02d}")


def test_ot_parent_must_match_same_client():
    _ensure_admin_user()
    client = _build_client()

    user_a = _create_user("ot-user-b@example.com")
    user_b = _create_user("ot-user-c@example.com")

    repair_a = client.post(
        "/api/v1/repairs/",
        json={"client_id": user_a, "title": "A", "description": "A"},
    )
    repair_b = client.post(
        "/api/v1/repairs/",
        json={"client_id": user_b, "title": "B", "description": "B"},
    )
    assert repair_a.status_code in (200, 201)
    assert repair_b.status_code in (200, 201)

    parent_b_id = int(repair_b.json()["id"])

    invalid_group = client.post(
        "/api/v1/repairs/",
        json={
            "client_id": user_a,
            "title": "A child invalid",
            "description": "invalid",
            "ot_parent_id": parent_b_id,
        },
    )
    assert invalid_group.status_code == 400


def test_reserve_consume_and_release_stock_flow():
    _ensure_admin_user()
    client = _build_client()

    user_id = _create_user("ot-user-d@example.com")
    repair_res = client.post(
        "/api/v1/repairs/",
        json={"client_id": user_id, "title": "Reserve flow", "description": "reserve test"},
    )
    assert repair_res.status_code in (200, 201)
    repair_id = int(repair_res.json()["id"])

    db = SessionLocal()
    try:
        category = db.query(Category).order_by(Category.id.asc()).first()
        if not category:
            category = Category(name="OT Test Category", description="Category for OT workflow tests")
            db.add(category)
            db.commit()
            db.refresh(category)

        product = db.query(Product).filter(Product.sku == "OT-RES-001").first()
        if not product:
            product = Product(
                name="Test Capacitor",
                sku="OT-RES-001",
                category_id=category.id,
                quantity=10,
                min_quantity=1,
                price=100,
            )
            db.add(product)
            db.commit()
            db.refresh(product)

        stock = db.query(Stock).filter(
            Stock.component_table == "products",
            Stock.component_id == product.id,
        ).first()
        if not stock:
            stock = Stock(
                component_table="products",
                component_id=product.id,
                quantity=10,
                quantity_reserved=0,
                minimum_stock=1,
            )
            db.add(stock)
        else:
            stock.quantity = 10
            stock.quantity_reserved = 0
        db.commit()
        product_id = int(product.id)
    finally:
        db.close()

    reserve_res = client.post(
        f"/api/v1/repairs/{repair_id}/components/reserve",
        json={
            "component_table": "products",
            "component_id": product_id,
            "quantity": 2,
            "notes": "Reserva inicial",
        },
    )
    assert reserve_res.status_code in (200, 201)
    reserve_body = reserve_res.json()
    assert reserve_body["ok"] is True
    assert int(reserve_body["total_reserved"]) >= 2

    consume_res = client.post(
        f"/api/v1/repairs/{repair_id}/components",
        json={
            "component_table": "products",
            "component_id": product_id,
            "quantity": 1,
            "from_reserved": True,
            "notes": "Consumir reservado",
        },
    )
    assert consume_res.status_code in (200, 201)

    release_res = client.post(
        f"/api/v1/repairs/{repair_id}/components/release",
        json={
            "component_table": "products",
            "component_id": product_id,
            "quantity": 1,
            "notes": "Liberar remanente",
        },
    )
    assert release_res.status_code == 200
    assert release_res.json()["ok"] is True

    db = SessionLocal()
    try:
        stock = db.query(Stock).filter(
            Stock.component_table == "products",
            Stock.component_id == product_id,
        ).first()
        assert stock is not None
        assert int(stock.quantity) == 9
        assert int(stock.quantity_reserved or 0) == 0

        movement_types = {
            row.movement_type
            for row in db.query(StockMovement)
            .filter(StockMovement.repair_id == repair_id)
            .all()
        }
        assert "RESERVE" in movement_types
        assert "OUT_RESERVED" in movement_types
        assert "UNRESERVE" in movement_types
    finally:
        db.close()
