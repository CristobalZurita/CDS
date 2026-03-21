from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.inventory import Product
from app.models.stock import Stock

try:
    from app.services.cloudinary_service import resolve_image_url

    CLOUDINARY_AVAILABLE = True
except ImportError:
    CLOUDINARY_AVAILABLE = False

    def resolve_image_url(path):
        return path


_STORE_EXCLUDED_TERMS = (
    "teclado",
    "keyboard",
    "herramient",
    "insumo",
)


def _load_store_catalog_sync_module():
    repo_root = Path(__file__).resolve().parents[3]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    import scripts.sync_store_catalog_from_inventory_images as sync_module

    return sync_module


def parse_product_meta(description: Optional[str]) -> dict:
    if not description:
        return {}
    text = str(description).strip()
    if not text.startswith("{"):
        return {}
    try:
        payload = json.loads(text)
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def sku_family(sku: Optional[str]) -> Optional[str]:
    if not sku:
        return None
    prefix = str(sku).strip().split("-", 1)[0].upper()
    return prefix or None


def product_store_default(product: Product, category_name: Optional[str] = None) -> bool:
    haystack = " ".join(
        [
            str(product.sku or ""),
            str(product.name or ""),
            str(category_name or ""),
        ]
    ).lower()
    return not any(term in haystack for term in _STORE_EXCLUDED_TERMS)


def enabled_from_meta(meta: dict, product: Product, category_name: Optional[str] = None) -> bool:
    if "enabled" in meta:
        return bool(meta.get("enabled"))
    return product_store_default(product, category_name)


def store_visible_from_meta(meta: dict, product: Product, category_name: Optional[str] = None) -> bool:
    enabled = enabled_from_meta(meta, product, category_name)
    if not enabled:
        return False
    if "store_visible" in meta:
        return bool(meta.get("store_visible"))
    return False


def merge_product_meta(product: Product, payload: dict) -> Optional[str]:
    raw_description = payload.get("description") if "description" in payload else product.description
    meta = parse_product_meta(raw_description)
    plain_text = None

    if not meta:
        text = str(raw_description or "").strip()
        if text:
            plain_text = text
    else:
        text = str(meta.get("text") or "").strip()
        if text:
            plain_text = text

    changed = False
    if "enabled" in payload:
        if plain_text and "text" not in meta:
            meta["text"] = plain_text
        meta["enabled"] = bool(payload.get("enabled"))
        changed = True
    if "store_visible" in payload:
        if plain_text and "text" not in meta:
            meta["text"] = plain_text
        meta["store_visible"] = bool(payload.get("store_visible"))
        changed = True
    if "origin_status" in payload and payload.get("origin_status") is not None:
        if plain_text and "text" not in meta:
            meta["text"] = plain_text
        meta["origin_status"] = str(payload.get("origin_status")).strip()
        changed = True

    if not changed:
        return raw_description
    return json.dumps(meta, ensure_ascii=False)


def stock_alert_level(available_qty: int, min_stock: int) -> Optional[str]:
    if min_stock <= 0:
        return None
    if available_qty <= max(1, int(min_stock * 0.05)):
        return "critical_5"
    if available_qty <= max(1, int(min_stock * 0.2)):
        return "high_20"
    if available_qty <= max(1, int(min_stock * 0.5)):
        return "medium_50"
    if available_qty <= min_stock:
        return "low_min"
    return None


def public_stock_label(sellable_stock: int) -> str:
    if sellable_stock <= 0:
        return "agotado"
    if sellable_stock <= 2:
        return "ultimas_unidades"
    if sellable_stock <= 5:
        return "stock_bajo"
    return "disponible"


def serialize_inventory_product(db: Session, product: Product) -> dict:
    meta = parse_product_meta(product.description)
    product_family = sku_family(product.sku)
    product_origin = str(meta.get("origin_status") or "").strip().upper() or None
    category = db.query(Category).filter(Category.id == product.category_id).first()
    category_name = category.name if category else None
    product_enabled = enabled_from_meta(meta, product, category_name)
    product_store_visible = store_visible_from_meta(meta, product, category_name)

    stock = (
        db.query(Stock)
        .filter(
            Stock.component_table == "products",
            Stock.component_id == product.id,
        )
        .first()
    )

    stock_qty = stock.quantity if stock else product.quantity
    available_qty = stock.available_quantity if stock else product.quantity
    min_stock = stock.minimum_stock if stock else product.min_quantity
    sellable_stock = max(int(available_qty or 0) - int(min_stock or 0), 0)
    alert_level = stock_alert_level(int(available_qty or 0), int(min_stock or 0))
    image_url_resolved = resolve_image_url(product.image_url) if CLOUDINARY_AVAILABLE else product.image_url

    return {
        "id": product.id,
        "stock_id": stock.id if stock else None,
        "name": product.name,
        "sku": product.sku,
        "description": product.description,
        "family": product_family,
        "category": category_name,
        "category_id": product.category_id,
        "origin_status": product_origin,
        "enabled": product_enabled,
        "store_visible": product_store_visible,
        "kicad_symbol": meta.get("kicad_symbol"),
        "kicad_footprint_default": meta.get("kicad_footprint_default"),
        "stock": stock_qty,
        "available_stock": available_qty,
        "sellable_stock": sellable_stock,
        "stock_unit": "u",
        "image_url": image_url_resolved,
        "price": product.price,
        "min_stock": min_stock,
        "is_low_stock": available_qty <= min_stock,
        "stock_alert_level": alert_level,
        "quantity_reserved": stock.quantity_reserved if stock else 0,
        "quantity_in_transit": stock.quantity_in_transit if stock else 0,
        "quantity_damaged": stock.quantity_damaged if stock else 0,
        "quantity_in_work": stock.quantity_in_work if stock else 0,
        "quantity_under_review": stock.quantity_under_review if stock else 0,
        "quantity_internal_use": stock.quantity_internal_use if stock else 0,
        "location": stock.bin_code if stock else None,
        "supplier": stock.supplier if stock else None,
        "unit_cost": stock.unit_cost if stock else product.price,
    }


def list_inventory_payloads(
    db: Session,
    *,
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    family: Optional[str] = None,
    origin_status: Optional[str] = None,
    enabled_only: bool = False,
    low_stock_only: bool = False,
) -> list[dict]:
    query = db.query(Product)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Product.name.ilike(search_term))
            | (Product.sku.ilike(search_term))
            | (Product.description.ilike(search_term))
        )

    if category_id:
        query = query.filter(Product.category_id == category_id)

    products = query.order_by(Product.name).all()
    family_filter = str(family).strip().upper() if family else None
    origin_filter = str(origin_status).strip().upper() if origin_status else None

    result = []
    for product in products:
        serialized = serialize_inventory_product(db, product)

        if family_filter and serialized["family"] != family_filter:
            continue
        if origin_filter and serialized["origin_status"] != origin_filter:
            continue
        if enabled_only and serialized["enabled"] is not True:
            continue
        if low_stock_only and serialized["available_stock"] > serialized["min_stock"]:
            continue

        result.append(serialized)

    return result


def inventory_alerts_summary(db: Session) -> dict:
    products = db.query(Product).order_by(Product.name).all()
    levels = {
        "critical_5": [],
        "high_20": [],
        "medium_50": [],
        "low_min": [],
    }

    for product in products:
        serialized = serialize_inventory_product(db, product)
        level = serialized.get("stock_alert_level")
        if not level:
            continue
        levels[level].append(
            {
                "id": serialized["id"],
                "sku": serialized["sku"],
                "name": serialized["name"],
                "available_stock": serialized["available_stock"],
                "min_stock": serialized["min_stock"],
                "sellable_stock": serialized["sellable_stock"],
                "store_visible": serialized["store_visible"],
                "level": level,
            }
        )

    return {
        "critical_5": levels["critical_5"],
        "high_20": levels["high_20"],
        "medium_50": levels["medium_50"],
        "low_min": levels["low_min"],
        "counts": {key: len(value) for key, value in levels.items()},
    }


def list_public_catalog_payload(
    db: Session,
    *,
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    family: Optional[str] = None,
    origin_status: Optional[str] = None,
    enabled_only: bool = True,
    in_stock_only: bool = True,
    limit: int = 120,
) -> list[dict]:
    query = db.query(Product)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Product.name.ilike(search_term))
            | (Product.sku.ilike(search_term))
            | (Product.description.ilike(search_term))
        )

    if category_id:
        query = query.filter(Product.category_id == category_id)

    products = query.order_by(Product.name).all()
    family_filter = str(family).strip().upper() if family else None
    origin_filter = str(origin_status).strip().upper() if origin_status else None

    result = []
    for product in products:
        serialized = serialize_inventory_product(db, product)
        sellable_stock = int(serialized["sellable_stock"] or 0)
        label = public_stock_label(sellable_stock)

        if family_filter and serialized["family"] != family_filter:
            continue
        if origin_filter and serialized["origin_status"] != origin_filter:
            continue
        if enabled_only and serialized["enabled"] is not True:
            continue
        if serialized["store_visible"] is not True:
            continue
        if in_stock_only and sellable_stock <= 0:
            continue

        result.append(
            {
                "id": serialized["id"],
                "name": serialized["name"],
                "sku": serialized["sku"],
                "description": serialized["description"],
                "family": serialized["family"],
                "category": serialized["category"],
                "category_id": serialized["category_id"],
                "origin_status": serialized["origin_status"],
                "enabled": serialized["enabled"],
                "store_visible": serialized["store_visible"],
                "available_stock": serialized["available_stock"],
                "sellable_stock": sellable_stock,
                "stock_unit": serialized["stock_unit"],
                "stock_label": label,
                "image_url": serialized["image_url"],
                "price": serialized["price"],
                "is_low_stock": serialized["is_low_stock"],
                "min_stock": serialized["min_stock"],
                "stock_alert_level": serialized["stock_alert_level"],
            }
        )
        if len(result) >= limit:
            break

    return result


def get_store_catalog_status_payload() -> dict:
    return _load_store_catalog_sync_module().build_catalog_status()


def sync_store_catalog_payload() -> dict:
    sync_module = _load_store_catalog_sync_module()
    result = sync_module.sync_catalog(apply_changes=True)
    status_payload = sync_module.build_catalog_status()
    return {
        "ok": True,
        "result": result,
        "status": status_payload,
    }


def low_stock_alerts_payload(db: Session) -> list[dict]:
    products = db.query(Product).all()
    alerts = []
    for product in products:
        stock = (
            db.query(Stock)
            .filter(
                Stock.component_table == "products",
                Stock.component_id == product.id,
            )
            .first()
        )

        available_qty = stock.available_quantity if stock else product.quantity
        min_stock = stock.minimum_stock if stock else product.min_quantity
        level = stock_alert_level(int(available_qty or 0), int(min_stock or 0))

        if level:
            category = db.query(Category).filter(Category.id == product.category_id).first()
            alerts.append(
                {
                    "id": product.id,
                    "name": product.name,
                    "sku": product.sku,
                    "category": category.name if category else None,
                    "stock": stock.quantity if stock else product.quantity,
                    "available_stock": available_qty,
                    "min_stock": min_stock,
                    "sellable_stock": max(int(available_qty or 0) - int(min_stock or 0), 0),
                    "deficit": max(int(min_stock or 0) - int(available_qty or 0), 0),
                    "urgency": level,
                }
            )

    severity_order = {"critical_5": 0, "high_20": 1, "medium_50": 2, "low_min": 3}
    alerts.sort(key=lambda x: (severity_order.get(x["urgency"], 99), x["available_stock"]))
    return alerts
