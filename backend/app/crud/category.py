"""CRUD for Category."""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def create_category(db: Session, payload: CategoryCreate) -> Category:
    category = Category(name=payload.name, description=payload.description)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def get_category(db: Session, category_id: int) -> Optional[Category]:
    return db.query(Category).filter(Category.id == category_id).first()


def list_categories(db: Session, skip: int = 0, limit: int = 100) -> List[Category]:
    return db.query(Category).offset(skip).limit(limit).all()


def update_category(db: Session, category_id: int, payload: CategoryUpdate) -> Optional[Category]:
    category = get_category(db, category_id)
    if not category:
        return None
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(category, key, value)
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: int) -> bool:
    category = get_category(db, category_id)
    if not category:
        return False
    db.delete(category)
    db.commit()
    return True
