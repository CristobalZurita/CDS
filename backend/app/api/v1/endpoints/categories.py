"""Category endpoints (API v1)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryRead
from app.crud.category import create_category, list_categories, get_category, update_category, delete_category

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=List[CategoryRead])
def list_categories_endpoint(db: Session = Depends(get_db)):
    return list_categories(db)


@router.get("/{category_id}", response_model=CategoryRead)
def get_category_endpoint(category_id: int, db: Session = Depends(get_db)):
    category = get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category_endpoint(payload: CategoryCreate, db: Session = Depends(get_db)):
    return create_category(db, payload)


@router.put("/{category_id}", response_model=CategoryRead)
def update_category_endpoint(category_id: int, payload: CategoryUpdate, db: Session = Depends(get_db)):
    category = update_category(db, category_id, payload)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.delete("/{category_id}")
def delete_category_endpoint(category_id: int, db: Session = Depends(get_db)):
    ok = delete_category(db, category_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"ok": True}
