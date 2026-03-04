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


def _delete_product_by_sku(db, sku: str):
    product = db.query(Product).filter(Product.sku == sku).first()
    if not product:
        return

    stock = db.query(Stock).filter(
        Stock.component_table == "products",
        Stock.component_id == product.id,
    ).first()
    if stock:
        db.delete(stock)

    db.delete(product)
    db.commit()


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

    _delete_product_by_sku(db, "TEST_AUDIO_JACK_CHASIS_MONO_6_3")

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


def test_list_public_catalog_exposes_stock_label_and_sellable_stock(db):
    from app.routers.inventory import list_public_catalog

    category = db.query(Category).filter(Category.name == "Capacitores").first()
    if not category:
        category = Category(name="Capacitores", description="Capacitores test")
        db.add(category)
        db.commit()
        db.refresh(category)

    _delete_product_by_sku(db, "TEST-CAP-100UF-PUBLIC")

    product = Product(
        category_id=category.id,
        name="Capacitor 100uF Test Public",
        sku="TEST-CAP-100UF-PUBLIC",
        description=json.dumps({"enabled": True, "store_visible": True}, ensure_ascii=False),
        price=890,
        quantity=5,
        min_quantity=0,
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    stock = Stock(
        component_table="products",
        component_id=product.id,
        quantity=5,
        minimum_stock=3,
    )
    db.add(stock)
    db.commit()

    payload = list_public_catalog(
        db=db,
        enabled_only=True,
        in_stock_only=False,
        limit=120,
    )

    public_product = next(item for item in payload if item["id"] == product.id)
    assert public_product["sellable_stock"] == 2
    assert public_product["stock_label"] == "ultimas_unidades"


def test_list_public_catalog_hides_products_without_sellable_stock_when_filtered(db):
    from app.routers.inventory import list_public_catalog

    category = db.query(Category).filter(Category.name == "Conectores").first()
    if not category:
        category = Category(name="Conectores", description="Conectores test")
        db.add(category)
        db.commit()
        db.refresh(category)

    _delete_product_by_sku(db, "TEST-JACK-RESERVADO")

    product = Product(
        category_id=category.id,
        name="Jack reservado taller test",
        sku="TEST-JACK-RESERVADO",
        description=json.dumps({"enabled": True, "store_visible": True}, ensure_ascii=False),
        price=1500,
        quantity=4,
        min_quantity=0,
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    stock = Stock(
        component_table="products",
        component_id=product.id,
        quantity=4,
        minimum_stock=4,
    )
    db.add(stock)
    db.commit()

    filtered_payload = list_public_catalog(
        db=db,
        enabled_only=True,
        in_stock_only=True,
        limit=120,
    )
    unfiltered_payload = list_public_catalog(
        db=db,
        enabled_only=True,
        in_stock_only=False,
        limit=120,
    )

    assert all(item["id"] != product.id for item in filtered_payload)
    public_product = next(item for item in unfiltered_payload if item["id"] == product.id)
    assert public_product["sellable_stock"] == 0
    assert public_product["stock_label"] == "agotado"
