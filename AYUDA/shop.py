"""
backend/app/routers/shop.py

Router público de la tienda.
Agregar en app/main.py:
    from app.routers import shop
    app.include_router(shop.router)
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import math

from app.core.database import get_db
from app.models.category import Category
from app.models.product  import Product      # modelo existente
# from app.models.order import Order, OrderItem  # descomentar cuando crees el modelo

router = APIRouter(prefix="/api/v1/shop", tags=["shop"])


# ─── Schemas ────────────────────────────────────────────────

class CategoryOut(BaseModel):
    id:            int
    name:          str
    description:   Optional[str] = None
    product_count: int = 0

    class Config:
        from_attributes = True


class ProductOut(BaseModel):
    id:          int
    sku:         Optional[str] = None
    name:        str
    description: Optional[str] = None
    price:       float
    stock:       Optional[int] = None
    image_url:   Optional[str] = None
    category_id: Optional[int] = None
    category:    Optional[CategoryOut] = None

    class Config:
        from_attributes = True


class ProductsPage(BaseModel):
    items: List[ProductOut]
    total: int
    page:  int
    pages: int


class OrderItemIn(BaseModel):
    product_id: int
    qty:        int
    unit_price: float


class CustomerIn(BaseModel):
    name:  str
    email: EmailStr
    phone: str
    rut:   Optional[str] = None


class ShippingIn(BaseModel):
    address:  str
    commune:  str
    region:   str


class OrderIn(BaseModel):
    customer:       CustomerIn
    shipping:       ShippingIn
    items:          List[OrderItemIn]
    notes:          Optional[str]  = None
    payment_method: str            = "transfer"   # webpay | transfer | store


# ─── Endpoints ──────────────────────────────────────────────

@router.get("/categories", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    """Todas las categorías con conteo de productos en stock."""
    categories = db.query(Category).order_by(Category.name).all()

    result = []
    for cat in categories:
        count = (
            db.query(func.count(Product.id))
            .filter(Product.category_id == cat.id)
            .scalar() or 0
        )
        result.append(CategoryOut(
            id=cat.id,
            name=cat.name,
            description=cat.description,
            product_count=count,
        ))
    return result


@router.get("/products", response_model=ProductsPage)
def list_products(
    category_id: Optional[int]  = Query(None),
    search:      Optional[str]  = Query(None),
    page:        int            = Query(1,  ge=1),
    limit:       int            = Query(24, ge=1, le=100),
    sort:        str            = Query("name"),  # name|price_asc|price_desc|newest
    db:          Session        = Depends(get_db),
):
    q = (
        db.query(Product)
        .options(joinedload(Product.category))
        .filter(Product.stock > 0)    # sólo con stock; quita si quieres mostrar todo
    )

    if category_id:
        q = q.filter(Product.category_id == category_id)

    if search and search.strip():
        term = f"%{search.strip()}%"
        q = q.filter(
            or_(
                Product.name.ilike(term),
                Product.sku.ilike(term),
                Product.description.ilike(term),
            )
        )

    sort_map = {
        "name":       Product.name.asc(),
        "price_asc":  Product.price.asc(),
        "price_desc": Product.price.desc(),
        "newest":     Product.id.desc(),
    }
    q = q.order_by(sort_map.get(sort, Product.name.asc()))

    total  = q.count()
    pages  = max(1, math.ceil(total / limit))
    page   = min(page, pages)
    items  = q.offset((page - 1) * limit).limit(limit).all()

    return ProductsPage(
        items=[ProductOut.model_validate(p) for p in items],
        total=total,
        page=page,
        pages=pages,
    )


@router.get("/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = (
        db.query(Product)
        .options(joinedload(Product.category))
        .filter(Product.id == product_id)
        .first()
    )
    if not product:
        raise HTTPException(404, "Producto no encontrado")
    return ProductOut.model_validate(product)


@router.post("/orders", status_code=201)
def create_order(payload: OrderIn, db: Session = Depends(get_db)):
    """
    Crea un pedido, descuenta stock y retorna el código de seguimiento.
    Descomenta el bloque de Order/OrderItem cuando tengas ese modelo.
    """
    # Validar items y stock
    order_items = []
    total = 0.0
    for item_in in payload.items:
        product = db.query(Product).filter(Product.id == item_in.product_id).first()
        if not product:
            raise HTTPException(400, f"Producto {item_in.product_id} no encontrado")
        if (product.stock or 0) < item_in.qty:
            raise HTTPException(400, f"Stock insuficiente para '{product.name}'")
        total += item_in.unit_price * item_in.qty
        order_items.append((product, item_in.qty, item_in.unit_price))

    # Descontar stock
    for product, qty, _ in order_items:
        product.stock = (product.stock or 0) - qty
        db.add(product)

    db.commit()

    # TODO: crear Order/OrderItem en DB, enviar email de confirmación
    # Retorno provisional hasta implementar modelo Order
    return {
        "status":  "created",
        "total":   round(total, 0),
        "message": "Pedido recibido. Nos contactaremos para coordinar el pago.",
    }
