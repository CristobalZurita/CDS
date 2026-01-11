from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.models.category import Category
from backend.app.core.database import get_db

router = APIRouter(prefix="/api/categories", tags=["Categories"])

@router.get("/")
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()

@router.post("/")
def create_category(payload: dict, db: Session = Depends(get_db)):
    db_cat = Category(**payload)
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat

@router.put("/{category_id}")
def update_category(category_id: int, payload: dict, db: Session = Depends(get_db)):
    db_cat = db.query(Category).get(category_id)
    if not db_cat:
        raise HTTPException(status_code=404, detail="Category not found")
    for k, v in payload.items():
        setattr(db_cat, k, v)
    db.commit()
    db.refresh(db_cat)
    return db_cat

@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    db_cat = db.query(Category).get(category_id)
    if not db_cat:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(db_cat)
    db.commit()
    return {"ok": True}
