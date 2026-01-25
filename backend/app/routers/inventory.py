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
        available_qty = stock.available_quantity if stock else product.quantity

        # Filtrar por stock bajo si se solicita
        if low_stock_only:
            min_stock = stock.minimum_stock if stock else product.min_quantity
            if available_qty > min_stock:
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
            "available_stock": available_qty,
            "stock_unit": "u",  # Unidades por defecto
            "price": product.price,
            "min_stock": stock.minimum_stock if stock else product.min_quantity,
            "is_low_stock": available_qty <= (stock.minimum_stock if stock else product.min_quantity),
            "quantity_reserved": stock.quantity_reserved if stock else 0,
            "quantity_in_transit": stock.quantity_in_transit if stock else 0,
            "quantity_damaged": stock.quantity_damaged if stock else 0,
            "quantity_in_work": stock.quantity_in_work if stock else 0,
            "quantity_under_review": stock.quantity_under_review if stock else 0,
            "quantity_internal_use": stock.quantity_internal_use if stock else 0,
            "location": stock.bin_code if stock else None,
            "supplier": stock.supplier if stock else None,
            "unit_cost": stock.unit_cost if stock else product.price
        })

    return result


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
    )
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
    return {
        "id": product.id,
        "name": product.name,
        "sku": product.sku,
        "category_id": product.category_id,
        "stock": product.quantity,
        "price": product.price,
    }


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
    if "stock" in payload or "quantity" in payload:
        product.quantity = int(payload.get("stock") or payload.get("quantity") or 0)
    if "min_quantity" in payload and payload["min_quantity"] is not None:
        product.min_quantity = int(payload["min_quantity"])

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
    return {
        "id": product.id,
        "name": product.name,
        "sku": product.sku,
        "category_id": product.category_id,
        "stock": product.quantity,
        "price": product.price,
    }


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
        "available_stock": stock.available_quantity if stock else product.quantity,
        "stock_unit": "u",
        "price": product.price,
        "min_stock": stock.minimum_stock if stock else product.min_quantity,
        "is_low_stock": (stock.available_quantity if stock else product.quantity) <= (stock.minimum_stock if stock else product.min_quantity),
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
