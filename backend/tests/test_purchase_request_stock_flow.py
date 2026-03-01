import importlib
import json
from datetime import datetime

from fastapi.testclient import TestClient

import app.main as _main
from app.core.database import SessionLocal
from app.models.category import Category
from app.models.client import Client
from app.models.inventory import Product
from app.models.purchase_request import PurchaseRequestItem
from app.models.stock import Stock
from app.models.user import User


importlib.reload(_main)


def _build_client() -> TestClient:
    importlib.reload(_main)
    return TestClient(_main.app)


def _ensure_admin_user(user_email: str = "store-admin@example.com") -> int:
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.id == 1).first()
        if not admin:
            admin = User(
                id=1,
                email=user_email,
                username="storeadmin",
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

        client = db.query(Client).filter(Client.user_id == admin.id).first()
        if not client:
            client = Client(user_id=admin.id, name="Admin Cliente", email=user_email)
            db.add(client)
            db.commit()

        return int(admin.id)
    finally:
        db.close()


def _create_store_product(slug: str, quantity: int = 12, min_quantity: int = 3) -> int:
    db = SessionLocal()
    try:
        category = Category(name=f"Categoria Store {slug}", description="Categoria de prueba")
        db.add(category)
        db.commit()
        db.refresh(category)

        product = Product(
            category_id=category.id,
            name=f"Producto Store {slug}",
            sku=f"STORE-{slug.upper()}",
            description=json.dumps({"enabled": True, "store_visible": True}, ensure_ascii=False),
            price=2490,
            quantity=quantity,
            min_quantity=min_quantity,
        )
        db.add(product)
        db.commit()
        db.refresh(product)

        stock = Stock(
            component_table="products",
            component_id=product.id,
            quantity=quantity,
            minimum_stock=min_quantity,
            updated_at=datetime.utcnow(),
        )
        db.add(stock)
        db.commit()
        return int(product.id)
    finally:
        db.close()


def test_store_request_reserves_and_received_consumes_stock():
    _ensure_admin_user()
    client = _build_client()
    slug = datetime.utcnow().strftime("%H%M%S%f")
    product_id = _create_store_product(slug, quantity=12, min_quantity=3)

    create_res = client.post(
        "/api/v1/client/store/purchase-requests",
        json={
            "shipping_key": "pickup",
            "shipping_label": "Retiro en taller",
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 2,
                }
            ],
        },
    )
    assert create_res.status_code in (200, 201)
    request_id = int(create_res.json()["request"]["id"])

    inventory_after_create = client.get(f"/api/v1/inventory/{product_id}")
    assert inventory_after_create.status_code == 200
    assert inventory_after_create.json()["quantity_reserved"] == 2
    assert inventory_after_create.json()["stock"] == 12

    db = SessionLocal()
    try:
        item = db.query(PurchaseRequestItem).filter(PurchaseRequestItem.request_id == request_id).first()
        assert item is not None
        assert int(item.reserved_quantity or 0) == 2
    finally:
        db.close()

    received_res = client.patch(
        f"/api/v1/purchase-requests/{request_id}",
        json={"status": "received"},
    )
    assert received_res.status_code == 200

    inventory_after_receive = client.get(f"/api/v1/inventory/{product_id}")
    assert inventory_after_receive.status_code == 200
    payload = inventory_after_receive.json()
    assert payload["quantity_reserved"] == 0
    assert payload["stock"] == 10

    db = SessionLocal()
    try:
        item = db.query(PurchaseRequestItem).filter(PurchaseRequestItem.request_id == request_id).first()
        assert item is not None
        assert int(item.reserved_quantity or 0) == 0
    finally:
        db.close()


def test_store_request_cancel_releases_reserved_stock():
    _ensure_admin_user()
    client = _build_client()
    slug = datetime.utcnow().strftime("%H%M%S%f")
    product_id = _create_store_product(slug, quantity=9, min_quantity=2)

    create_res = client.post(
        "/api/v1/client/store/purchase-requests",
        json={
            "shipping_key": "manual",
            "shipping_label": "Despacho manual",
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 3,
                }
            ],
        },
    )
    assert create_res.status_code in (200, 201)
    request_id = int(create_res.json()["request"]["id"])

    inventory_after_create = client.get(f"/api/v1/inventory/{product_id}")
    assert inventory_after_create.status_code == 200
    assert inventory_after_create.json()["quantity_reserved"] == 3

    cancel_res = client.patch(
        f"/api/v1/purchase-requests/{request_id}",
        json={"status": "cancelled"},
    )
    assert cancel_res.status_code == 200

    inventory_after_cancel = client.get(f"/api/v1/inventory/{product_id}")
    assert inventory_after_cancel.status_code == 200
    payload = inventory_after_cancel.json()
    assert payload["quantity_reserved"] == 0
    assert payload["stock"] == 9

    db = SessionLocal()
    try:
        item = db.query(PurchaseRequestItem).filter(PurchaseRequestItem.request_id == request_id).first()
        assert item is not None
        assert int(item.reserved_quantity or 0) == 0
    finally:
        db.close()
