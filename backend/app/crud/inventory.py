"""CRUD for Product inventory."""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.inventory import Product
from app.schemas.inventory import ProductCreate, ProductUpdate


def create_product(db: Session, payload: ProductCreate) -> Product:
    product = Product(**payload.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def get_product(db: Session, product_id: int) -> Optional[Product]:
    return db.query(Product).filter(Product.id == product_id).first()


def list_products(db: Session, skip: int = 0, limit: int = 100) -> List[Product]:
    return db.query(Product).offset(skip).limit(limit).all()


def update_product(db: Session, product_id: int, payload: ProductUpdate) -> Optional[Product]:
    product = get_product(db, product_id)
    if not product:
        return None
    data = payload.dict(exclude_unset=True)
    for key, value in data.items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product_id: int) -> bool:
    product = get_product(db, product_id)
    if not product:
        return False
    db.delete(product)
    db.commit()
    return True
