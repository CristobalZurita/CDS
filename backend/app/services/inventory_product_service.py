from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.inventory import Product
from app.models.stock import Stock
from app.schemas.inventory import ItemSummary
from app.services.inventory_catalog_service import merge_product_meta


def get_product_or_404(
    db: Session,
    product_id: int,
    *,
    detail: str = "Producto no encontrado",
) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    return product


def ensure_unique_sku(
    db: Session,
    sku: str,
    *,
    exclude_product_id: int | None = None,
    detail: str | None = None,
) -> None:
    existing = db.query(Product).filter(Product.sku == sku).first()
    if existing and existing.id != exclude_product_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail or f"SKU '{sku}' ya existe",
        )


def ensure_product_stock(db: Session, product: Product) -> Stock:
    stock = db.query(Stock).filter(
        Stock.component_table == "products",
        Stock.component_id == product.id,
    ).first()
    if stock:
        return stock

    stock = Stock(
        component_table="products",
        component_id=product.id,
        quantity=int(product.quantity or 0),
        minimum_stock=int(product.min_quantity or 0),
    )
    db.add(stock)
    db.flush()
    return stock


def build_create_product_changes(payload: dict) -> dict:
    required = ("name", "sku", "category_id", "price")
    for field in required:
        if not payload.get(field):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing field: {field}",
            )

    description = merge_product_meta(
        Product(description=payload.get("description")),
        payload,
    )
    return {
        "category_id": int(payload["category_id"]),
        "name": payload["name"],
        "sku": payload["sku"],
        "description": description,
        "price": int(payload.get("price") or 0),
        "quantity": int(payload.get("stock") or payload.get("quantity") or 0),
        "min_quantity": int(payload.get("min_quantity") or 5),
        "image_url": payload.get("image_url"),
    }


def build_update_product_changes(product: Product, payload: dict) -> dict:
    changes = dict(payload)
    if {
        "description",
        "enabled",
        "store_visible",
        "origin_status",
    }.intersection(payload):
        current_payload = dict(payload)
        current_payload["description"] = payload.get("description", product.description)
        changes["description"] = merge_product_meta(product, current_payload)
    return changes


def build_item_summary(
    product: Product,
    *,
    category_name: str | None = None,
    stock_quantity: int | None = None,
) -> ItemSummary:
    return ItemSummary(
        id=product.id,
        sku=product.sku,
        name=product.name,
        category=category_name or "unknown",
        stock=int((stock_quantity if stock_quantity is not None else product.quantity) or 0),
    )


def list_item_summaries(
    db: Session,
    *,
    limit: int = 20,
    page: int = 1,
    category: str | None = None,
) -> list[ItemSummary]:
    query = (
        db.query(Product, Category.name, Stock.quantity)
        .outerjoin(Category, Product.category_id == Category.id)
        .outerjoin(
            Stock,
            and_(
                Stock.component_table == "products",
                Stock.component_id == Product.id,
            ),
        )
    )
    if category:
        query = query.filter(Category.name.ilike(f"%{category}%"))

    rows = (
        query
        .order_by(Product.name.asc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    return [
        build_item_summary(
            product,
            category_name=category_name,
            stock_quantity=stock_quantity,
        )
        for product, category_name, stock_quantity in rows
    ]


def get_item_summary_or_404(
    db: Session,
    product_id: int,
    *,
    detail: str = "Item not found",
) -> ItemSummary:
    row = (
        db.query(Product, Category.name, Stock.quantity)
        .outerjoin(Category, Product.category_id == Category.id)
        .outerjoin(
            Stock,
            and_(
                Stock.component_table == "products",
                Stock.component_id == Product.id,
            ),
        )
        .filter(Product.id == product_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

    product, category_name, stock_quantity = row
    return build_item_summary(
        product,
        category_name=category_name,
        stock_quantity=stock_quantity,
    )


def create_product_record(
    db: Session,
    *,
    category_id: int,
    name: str,
    sku: str,
    description: str | None = None,
    price: int,
    quantity: int = 0,
    min_quantity: int = 5,
    image_url: str | None = None,
) -> Product:
    ensure_unique_sku(db, sku)

    product = Product(
        category_id=int(category_id),
        name=name,
        sku=sku,
        description=description,
        price=int(price),
        quantity=int(quantity),
        min_quantity=int(min_quantity),
        image_url=image_url,
    )

    try:
        db.add(product)
        db.flush()
        ensure_product_stock(db, product)
        db.commit()
        db.refresh(product)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad: verificar category_id existe",
        )

    return product


def update_product_record(
    db: Session,
    product: Product,
    changes: dict,
) -> Product:
    sku = changes.get("sku")
    if sku and sku != product.sku:
        ensure_unique_sku(db, sku, exclude_product_id=product.id)

    if "category_id" in changes and changes["category_id"] is not None:
        product.category_id = int(changes["category_id"])
    if "name" in changes and changes["name"] is not None:
        product.name = changes["name"]
    if "sku" in changes and changes["sku"] is not None:
        product.sku = changes["sku"]
    if "description" in changes:
        product.description = changes.get("description")
    if "price" in changes and changes["price"] is not None:
        product.price = int(changes["price"])
    if "image_url" in changes:
        product.image_url = changes.get("image_url")
    if "stock" in changes or "quantity" in changes:
        product.quantity = int(changes.get("stock") or changes.get("quantity") or 0)
    if "min_quantity" in changes and changes["min_quantity"] is not None:
        product.min_quantity = int(changes["min_quantity"])

    stock = ensure_product_stock(db, product)
    if "stock" in changes or "quantity" in changes:
        stock.quantity = int(changes.get("stock") or changes.get("quantity") or 0)
    if "min_quantity" in changes and changes["min_quantity"] is not None:
        stock.minimum_stock = int(changes["min_quantity"])
    if "quantity_reserved" in changes:
        stock.quantity_reserved = int(changes.get("quantity_reserved") or 0)
    if "quantity_in_transit" in changes:
        stock.quantity_in_transit = int(changes.get("quantity_in_transit") or 0)
    if "quantity_damaged" in changes:
        stock.quantity_damaged = int(changes.get("quantity_damaged") or 0)
    if "quantity_in_work" in changes:
        stock.quantity_in_work = int(changes.get("quantity_in_work") or 0)
    if "quantity_under_review" in changes:
        stock.quantity_under_review = int(changes.get("quantity_under_review") or 0)
    if "quantity_internal_use" in changes:
        stock.quantity_internal_use = int(changes.get("quantity_internal_use") or 0)
    if "supplier" in changes:
        stock.supplier = changes.get("supplier")
    if "bin_code" in changes:
        stock.bin_code = changes.get("bin_code")
    if "unit_cost" in changes:
        stock.unit_cost = changes.get("unit_cost")

    try:
        db.commit()
        db.refresh(product)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad: verificar category_id existe",
        )

    return product


def delete_product_record(db: Session, product: Product) -> None:
    db.delete(product)
    db.commit()
