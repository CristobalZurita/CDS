"""
Router de Inventario
====================
Endpoints para consultar productos disponibles en inventario.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_permission
from app.models.inventory import Product
from app.models.stock import Stock
from app.models.category import Category

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("/")
def list_inventory(
    search: Optional[str] = None,
    category_id: Optional[int] = None,
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

    # Enriquecer con información de stock
    result = []
    for product in products:
        # Buscar stock para este producto
        stock = db.query(Stock).filter(
            Stock.component_table == "products",
            Stock.component_id == product.id
        ).first()

        stock_qty = stock.quantity if stock else product.quantity

        # Filtrar por stock bajo si se solicita
        if low_stock_only:
            min_stock = stock.minimum_stock if stock else product.min_quantity
            if stock_qty > min_stock:
                continue

        # Obtener nombre de categoría
        category = db.query(Category).filter(Category.id == product.category_id).first()

        result.append({
            "id": product.id,
            "name": product.name,
            "sku": product.sku,
            "description": product.description,
            "category": category.name if category else None,
            "category_id": product.category_id,
            "stock": stock_qty,
            "stock_unit": "u",  # Unidades por defecto
            "price": product.price,
            "min_stock": stock.minimum_stock if stock else product.min_quantity,
            "is_low_stock": stock_qty <= (stock.minimum_stock if stock else product.min_quantity),
            "location": stock.bin_code if stock else None,
            "supplier": stock.supplier if stock else None,
            "unit_cost": stock.unit_cost if stock else product.price
        })

    return result


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

    stock = db.query(Stock).filter(
        Stock.component_table == "products",
        Stock.component_id == product.id
    ).first()

    category = db.query(Category).filter(Category.id == product.category_id).first()

    return {
        "id": product.id,
        "name": product.name,
        "sku": product.sku,
        "description": product.description,
        "category": category.name if category else None,
        "category_id": product.category_id,
        "stock": stock.quantity if stock else product.quantity,
        "stock_unit": "u",
        "price": product.price,
        "min_stock": stock.minimum_stock if stock else product.min_quantity,
        "is_low_stock": (stock.quantity if stock else product.quantity) <= (stock.minimum_stock if stock else product.min_quantity),
        "location": stock.bin_code if stock else None,
        "supplier": stock.supplier if stock else None,
        "unit_cost": stock.unit_cost if stock else product.price
    }


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

        stock_qty = stock.quantity if stock else product.quantity
        min_stock = stock.minimum_stock if stock else product.min_quantity

        if stock_qty <= min_stock:
            category = db.query(Category).filter(Category.id == product.category_id).first()
            alerts.append({
                "id": product.id,
                "name": product.name,
                "sku": product.sku,
                "category": category.name if category else None,
                "stock": stock_qty,
                "min_stock": min_stock,
                "deficit": min_stock - stock_qty + 1,  # Cuánto falta para estar OK
                "urgency": "critical" if stock_qty == 0 else "warning"
            })

    # Ordenar por urgencia (críticos primero)
    alerts.sort(key=lambda x: (0 if x["urgency"] == "critical" else 1, x["stock"]))

    return alerts
