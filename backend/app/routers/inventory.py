"""
Router de Inventario
====================
Endpoints para consultar productos disponibles en inventario.
"""
import json
import sys
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_permission
from app.models.inventory import Product
from app.models.stock import Stock
from app.models.category import Category

# ADITIVO: Importar servicio de Cloudinary para resolver imágenes
try:
    from app.services.cloudinary_service import resolve_image_url
    CLOUDINARY_AVAILABLE = True
except ImportError:
    CLOUDINARY_AVAILABLE = False
    def resolve_image_url(path):
        return path

router = APIRouter(prefix="/inventory", tags=["Inventory"])

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


def _parse_product_meta(description: Optional[str]) -> dict:
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


def _sku_family(sku: Optional[str]) -> Optional[str]:
    if not sku:
        return None
    prefix = str(sku).strip().split("-", 1)[0].upper()
    return prefix or None


def _product_store_default(product: Product, category_name: Optional[str] = None) -> bool:
    haystack = " ".join(
        [
            str(product.sku or ""),
            str(product.name or ""),
            str(category_name or ""),
        ]
    ).lower()
    return not any(term in haystack for term in _STORE_EXCLUDED_TERMS)


def _enabled_from_meta(meta: dict, product: Product, category_name: Optional[str] = None) -> bool:
    if "enabled" in meta:
        return bool(meta.get("enabled"))
    return _product_store_default(product, category_name)


def _store_visible_from_meta(meta: dict, product: Product, category_name: Optional[str] = None) -> bool:
    enabled = _enabled_from_meta(meta, product, category_name)
    if not enabled:
        return False
    if "store_visible" in meta:
        return bool(meta.get("store_visible"))
    return False


def _merge_product_meta(product: Product, payload: dict) -> Optional[str]:
    raw_description = payload.get("description") if "description" in payload else product.description
    meta = _parse_product_meta(raw_description)
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


def _stock_alert_level(available_qty: int, min_stock: int) -> Optional[str]:
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


def _public_stock_label(sellable_stock: int) -> str:
    if sellable_stock <= 0:
        return "agotado"
    if sellable_stock <= 2:
        return "ultimas_unidades"
    if sellable_stock <= 5:
        return "stock_bajo"
    return "disponible"


def _serialize_inventory_product(db: Session, product: Product) -> dict:
    meta = _parse_product_meta(product.description)
    product_family = _sku_family(product.sku)
    product_origin = str(meta.get("origin_status") or "").strip().upper() or None
    category = db.query(Category).filter(Category.id == product.category_id).first()
    category_name = category.name if category else None
    product_enabled = _enabled_from_meta(meta, product, category_name)
    product_store_visible = _store_visible_from_meta(meta, product, category_name)

    stock = db.query(Stock).filter(
        Stock.component_table == "products",
        Stock.component_id == product.id
    ).first()

    stock_qty = stock.quantity if stock else product.quantity
    available_qty = stock.available_quantity if stock else product.quantity
    min_stock = stock.minimum_stock if stock else product.min_quantity
    sellable_stock = max(int(available_qty or 0) - int(min_stock or 0), 0)
    stock_alert_level = _stock_alert_level(int(available_qty or 0), int(min_stock or 0))

        # ADITIVO: Resolver imagen a Cloudinary si está disponible
    image_url_resolved = resolve_image_url(product.image_url) if CLOUDINARY_AVAILABLE else product.image_url

    return {
        "id": product.id,
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
        "stock_alert_level": stock_alert_level,
        "quantity_reserved": stock.quantity_reserved if stock else 0,
        "quantity_in_transit": stock.quantity_in_transit if stock else 0,
        "quantity_damaged": stock.quantity_damaged if stock else 0,
        "quantity_in_work": stock.quantity_in_work if stock else 0,
        "quantity_under_review": stock.quantity_under_review if stock else 0,
        "quantity_internal_use": stock.quantity_internal_use if stock else 0,
        "location": stock.bin_code if stock else None,
        "supplier": stock.supplier if stock else None,
        "unit_cost": stock.unit_cost if stock else product.price
    }


@router.get("", include_in_schema=False)
@router.get("/")
def list_inventory(
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    family: Optional[str] = None,
    origin_status: Optional[str] = None,
    enabled_only: bool = False,
    low_stock_only: bool = False,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("inventory", "read"))
):
    """
    Lista productos con información de stock.
    - search: Buscar por nombre, SKU o descripción
    - category_id: Filtrar por categoría
    - low_stock_only: Solo mostrar productos con stock bajo
    """
    # Query base de productos
    query = db.query(Product)

    # Aplicar filtros
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Product.name.ilike(search_term)) |
            (Product.sku.ilike(search_term)) |
            (Product.description.ilike(search_term))
        )

    if category_id:
        query = query.filter(Product.category_id == category_id)

    products = query.order_by(Product.name).all()
    family_filter = str(family).strip().upper() if family else None
    origin_filter = str(origin_status).strip().upper() if origin_status else None

    result = []
    for product in products:
        serialized = _serialize_inventory_product(db, product)
        product_family = serialized["family"]
        product_origin = serialized["origin_status"]
        product_enabled = serialized["enabled"]
        available_qty = serialized["available_stock"]
        min_stock = serialized["min_stock"]

        if family_filter and product_family != family_filter:
            continue
        if origin_filter and product_origin != origin_filter:
            continue
        if enabled_only and product_enabled is not True:
            continue

        # Filtrar por stock bajo si se solicita
        if low_stock_only:
            if available_qty > min_stock:
                continue

        result.append(serialized)

    return result


@router.get("/alerts/summary")
def get_inventory_alerts_summary(
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("inventory", "read"))
):
    products = db.query(Product).order_by(Product.name).all()
    levels = {
        "critical_5": [],
        "high_20": [],
        "medium_50": [],
        "low_min": [],
    }

    for product in products:
        serialized = _serialize_inventory_product(db, product)
        level = serialized.get("stock_alert_level")
        if not level:
            continue
        levels[level].append({
            "id": serialized["id"],
            "sku": serialized["sku"],
            "name": serialized["name"],
            "available_stock": serialized["available_stock"],
            "min_stock": serialized["min_stock"],
            "sellable_stock": serialized["sellable_stock"],
            "store_visible": serialized["store_visible"],
            "level": level,
        })

    return {
        "critical_5": levels["critical_5"],
        "high_20": levels["high_20"],
        "medium_50": levels["medium_50"],
        "low_min": levels["low_min"],
        "counts": {key: len(value) for key, value in levels.items()},
    }


@router.get("/public", include_in_schema=False)
@router.get("/public/")
def list_public_catalog(
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    family: Optional[str] = None,
    origin_status: Optional[str] = None,
    enabled_only: bool = Query(default=True),
    in_stock_only: bool = Query(default=True),
    limit: int = Query(default=120, ge=1, le=5000),
    db: Session = Depends(get_db),
):
    """
    Catálogo público de productos basado en la misma fuente de verdad del inventario.
    No expone permisos internos y por defecto sólo devuelve ítems habilitados y con stock.
    """
    query = db.query(Product)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Product.name.ilike(search_term)) |
            (Product.sku.ilike(search_term)) |
            (Product.description.ilike(search_term))
        )

    if category_id:
        query = query.filter(Product.category_id == category_id)

    products = query.order_by(Product.name).all()
    family_filter = str(family).strip().upper() if family else None
    origin_filter = str(origin_status).strip().upper() if origin_status else None

    result = []
    for product in products:
        serialized = _serialize_inventory_product(db, product)
        sellable_stock = int(serialized["sellable_stock"] or 0)
        stock_label = _public_stock_label(sellable_stock)

        if family_filter and serialized["family"] != family_filter:
            continue
        if origin_filter and serialized["origin_status"] != origin_filter:
            continue
        if enabled_only and serialized["enabled"] is not True:
            continue
        if serialized.get("store_visible") is not True:
            continue
        if in_stock_only and sellable_stock <= 0:
            continue

        result.append({
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
            "stock_label": stock_label,
            "image_url": serialized["image_url"],
            "price": serialized["price"],
            "is_low_stock": serialized["is_low_stock"],
            "min_stock": serialized["min_stock"],
            "stock_alert_level": serialized["stock_alert_level"],
        })
        if len(result) >= limit:
            break

    return result


@router.get("/store-catalog/status")
def get_store_catalog_status(
    user: dict = Depends(require_permission("inventory", "read"))
):
    sync_module = _load_store_catalog_sync_module()
    return sync_module.build_catalog_status()


@router.post("/store-catalog/sync")
def sync_store_catalog(
    user: dict = Depends(require_permission("inventory", "update"))
):
    sync_module = _load_store_catalog_sync_module()
    result = sync_module.sync_catalog(apply_changes=True)
    status_payload = sync_module.build_catalog_status()
    return {
        "ok": True,
        "result": result,
        "status": status_payload,
    }


@router.post("", status_code=status.HTTP_201_CREATED, include_in_schema=False)
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_inventory_item(
    payload: dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("inventory", "create"))
):
    """Crear producto en inventario."""
    required = ("name", "sku", "category_id", "price")
    for field in required:
        if not payload.get(field):
            raise HTTPException(status_code=400, detail=f"Missing field: {field}")

    product = Product(
        name=payload["name"],
        sku=payload["sku"],
        category_id=int(payload["category_id"]),
        description=payload.get("description"),
        price=int(payload.get("price") or 0),
        quantity=int(payload.get("stock") or payload.get("quantity") or 0),
        min_quantity=int(payload.get("min_quantity") or 5),
        image_url=payload.get("image_url"),
    )
    product.description = _merge_product_meta(product, payload)
    db.add(product)
    db.commit()
    db.refresh(product)
    # Crear stock extendido si no existe
    stock = db.query(Stock).filter(
        Stock.component_table == "products",
        Stock.component_id == product.id
    ).first()
    if not stock:
        stock = Stock(
            component_table="products",
            component_id=product.id,
            quantity=product.quantity,
            minimum_stock=product.min_quantity
        )
        db.add(stock)
        db.commit()
    db.refresh(product)
    return _serialize_inventory_product(db, product)


@router.put("/{product_id}")
def update_inventory_item(
    product_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("inventory", "update"))
):
    """Actualizar producto en inventario."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if "name" in payload:
        product.name = payload["name"]
    if "sku" in payload:
        product.sku = payload["sku"]
    if "description" in payload:
        product.description = payload["description"]
    if "category_id" in payload and payload["category_id"] is not None:
        product.category_id = int(payload["category_id"])
    if "price" in payload and payload["price"] is not None:
        product.price = int(payload["price"])
    if "image_url" in payload:
        product.image_url = payload.get("image_url")
    if "stock" in payload or "quantity" in payload:
        product.quantity = int(payload.get("stock") or payload.get("quantity") or 0)
    if "min_quantity" in payload and payload["min_quantity"] is not None:
        product.min_quantity = int(payload["min_quantity"])
    product.description = _merge_product_meta(product, payload)

    stock = db.query(Stock).filter(
        Stock.component_table == "products",
        Stock.component_id == product.id
    ).first()
    if not stock:
        stock = Stock(
            component_table="products",
            component_id=product.id,
            quantity=product.quantity,
            minimum_stock=product.min_quantity
        )
        db.add(stock)

    if "stock" in payload or "quantity" in payload:
        stock.quantity = int(payload.get("stock") or payload.get("quantity") or 0)
    if "min_quantity" in payload and payload["min_quantity"] is not None:
        stock.minimum_stock = int(payload["min_quantity"])
    if "quantity_reserved" in payload:
        stock.quantity_reserved = int(payload.get("quantity_reserved") or 0)
    if "quantity_in_transit" in payload:
        stock.quantity_in_transit = int(payload.get("quantity_in_transit") or 0)
    if "quantity_damaged" in payload:
        stock.quantity_damaged = int(payload.get("quantity_damaged") or 0)
    if "quantity_in_work" in payload:
        stock.quantity_in_work = int(payload.get("quantity_in_work") or 0)
    if "quantity_under_review" in payload:
        stock.quantity_under_review = int(payload.get("quantity_under_review") or 0)
    if "quantity_internal_use" in payload:
        stock.quantity_internal_use = int(payload.get("quantity_internal_use") or 0)
    if "supplier" in payload:
        stock.supplier = payload.get("supplier")
    if "bin_code" in payload:
        stock.bin_code = payload.get("bin_code")
    if "unit_cost" in payload:
        stock.unit_cost = payload.get("unit_cost")

    db.commit()
    db.refresh(product)
    return _serialize_inventory_product(db, product)


@router.delete("/{product_id}")
def delete_inventory_item(
    product_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("inventory", "delete"))
):
    """Eliminar producto de inventario."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    db.delete(product)
    db.commit()
    return {"ok": True}


@router.get("/{product_id}")
def get_inventory_item(
    product_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("inventory", "read"))
):
    """Obtiene detalle de un producto específico con su stock"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    return _serialize_inventory_product(db, product)


@router.get("/low-stock/alerts")
def get_low_stock_alerts(
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("inventory", "read"))
):
    """Obtiene lista de productos con stock bajo para alertas"""
    products = db.query(Product).all()

    alerts = []
    for product in products:
        stock = db.query(Stock).filter(
            Stock.component_table == "products",
            Stock.component_id == product.id
        ).first()

        available_qty = stock.available_quantity if stock else product.quantity
        min_stock = stock.minimum_stock if stock else product.min_quantity
        level = _stock_alert_level(int(available_qty or 0), int(min_stock or 0))

        if level:
            category = db.query(Category).filter(Category.id == product.category_id).first()
            alerts.append({
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
            })

    severity_order = {"critical_5": 0, "high_20": 1, "medium_50": 2, "low_min": 3}
    alerts.sort(key=lambda x: (severity_order.get(x["urgency"], 99), x["available_stock"]))

    return alerts
