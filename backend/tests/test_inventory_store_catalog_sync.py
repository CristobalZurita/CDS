import sys
import os
import json

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.routers.inventory import get_store_catalog_status, sync_store_catalog
from app.models.category import Category
from app.models.inventory import Product
from app.models.stock import Stock
import scripts.sync_store_catalog_from_inventory_images as sync_module


def test_get_store_catalog_status_uses_sync_status(monkeypatch):
    expected = {
        "files_count": 3,
        "linked_products_count": 2,
        "explicit_store_visible_count": 2,
        "with_nonzero_stock_count": 1,
        "sellable_now_count": 1,
        "pending_images_count": 1,
        "orphan_rows_count": 0,
        "pending_images": ["nuevo.webp"],
        "orphan_rows": [],
    }

    monkeypatch.setattr(sync_module, "build_catalog_status", lambda: expected)

    payload = get_store_catalog_status(user={"user_id": "1", "role": "admin"})

    assert payload == expected


def test_sync_store_catalog_returns_sync_result_and_status(monkeypatch):
    sync_result = {
        "images": 3,
        "matched": 2,
        "created": 1,
        "matched_items": [],
        "created_items": [],
    }
    status_payload = {
        "files_count": 3,
        "linked_products_count": 3,
        "explicit_store_visible_count": 3,
        "with_nonzero_stock_count": 1,
        "sellable_now_count": 1,
        "pending_images_count": 0,
        "orphan_rows_count": 0,
        "pending_images": [],
        "orphan_rows": [],
    }

    monkeypatch.setattr(sync_module, "sync_catalog", lambda apply_changes: sync_result)
    monkeypatch.setattr(sync_module, "build_catalog_status", lambda: status_payload)

    payload = sync_store_catalog(user={"user_id": "1", "role": "admin"})

    assert payload["ok"] is True
    assert payload["result"] == sync_result
    assert payload["status"] == status_payload


def test_sync_catalog_matches_prefixed_image_to_existing_product(db, monkeypatch, tmp_path):
    category = db.query(Category).filter(Category.name == "Conectores").first()
    if not category:
        category = Category(name="Conectores", description="Conectores E2E")
        db.add(category)
        db.commit()
        db.refresh(category)

    product = Product(
        category_id=category.id,
        name="Audio Jack Chasis Mono 6 3",
        sku="TEST_AUDIO_JACK_CHASIS_MONO_6_3",
        description=json.dumps({"enabled": True, "store_visible": True}, ensure_ascii=False),
        price=1000,
        quantity=4,
        min_quantity=0,
        image_url="/images/INVENTARIO/AUDIO_JACK_CHASIS_MONO_6_3.webp",
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    stock = Stock(
        component_table="products",
        component_id=product.id,
        quantity=4,
        minimum_stock=0,
    )
    db.add(stock)
    db.commit()

    image_dir = tmp_path / "INVENTARIO"
    image_dir.mkdir(parents=True, exist_ok=True)
    image_path = image_dir / "CONECTOR_AUDIO_JACK_CHASIS_MONO_6_3.webp"
    image_path.write_bytes(b"fake-image")

    monkeypatch.setattr(sync_module, "IMAGE_DIR", image_dir)

    result = sync_module.sync_catalog(apply_changes=True)
    db.refresh(product)
    db.refresh(stock)

    assert result["matched"] == 1
    assert result["created"] == 0
    assert product.image_url == f"/images/INVENTARIO/{image_path.name}"
