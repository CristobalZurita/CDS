"""
Router de Inventario
====================
Endpoints para consultar productos disponibles en inventario.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_permission
from app.services.inventory_catalog_service import (
    get_store_catalog_status_payload,
    inventory_alerts_summary,
    list_inventory_payloads,
    list_public_catalog_payload,
    low_stock_alerts_payload,
    serialize_inventory_product,
    sync_store_catalog_payload,
)
from app.services.inventory_product_service import (
    build_create_product_changes,
    build_update_product_changes,
    create_product_record,
    delete_product_record,
    get_product_or_404,
    update_product_record,
)

router = APIRouter(prefix="/inventory", tags=["Inventory"])


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
    return list_inventory_payloads(
        db,
        search=search,
        category_id=category_id,
        family=family,
        origin_status=origin_status,
        enabled_only=enabled_only,
        low_stock_only=low_stock_only,
    )


@router.get("/alerts/summary")
def get_inventory_alerts_summary(
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("inventory", "read"))
):
    return inventory_alerts_summary(db)


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
    return list_public_catalog_payload(
        db,
        search=search,
        category_id=category_id,
        family=family,
        origin_status=origin_status,
        enabled_only=enabled_only,
        in_stock_only=in_stock_only,
        limit=limit,
    )


@router.get("/store-catalog/status")
def get_store_catalog_status(
    user: dict = Depends(require_permission("inventory", "read"))
):
    return get_store_catalog_status_payload()


@router.post("/store-catalog/sync")
def sync_store_catalog(
    user: dict = Depends(require_permission("inventory", "update"))
):
    return sync_store_catalog_payload()


@router.post("", status_code=status.HTTP_201_CREATED, include_in_schema=False)
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_inventory_item(
    payload: dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("inventory", "create"))
):
    """Crear producto en inventario."""
    product = create_product_record(db, **build_create_product_changes(payload))
    return serialize_inventory_product(db, product)


@router.put("/{product_id}")
def update_inventory_item(
    product_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("inventory", "update"))
):
    """Actualizar producto en inventario."""
    product = get_product_or_404(db, product_id)
    product = update_product_record(db, product, build_update_product_changes(product, payload))
    return serialize_inventory_product(db, product)


@router.delete("/{product_id}")
def delete_inventory_item(
    product_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("inventory", "delete"))
):
    """Eliminar producto de inventario."""
    product = get_product_or_404(db, product_id)
    delete_product_record(db, product)
    return {"ok": True}


@router.get("/{product_id}")
def get_inventory_item(
    product_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("inventory", "read"))
):
    """Obtiene detalle de un producto específico con su stock"""
    product = get_product_or_404(db, product_id)
    return serialize_inventory_product(db, product)


@router.get("/low-stock/alerts")
def get_low_stock_alerts(
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("inventory", "read"))
):
    """Obtiene lista de productos con stock bajo para alertas"""
    return low_stock_alerts_payload(db)
