"""
Servicio de Category (aditivo, no destructivo).
Mantiene payload dict para compatibilidad con rutas actuales.
"""

from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.category_repository import CategoryRepository


class CategoryService:
    def __init__(self, db: Session):
        self.repo = CategoryRepository(db)

    def list_categories(self):
        return self.repo.list_all()

    def create_category(self, payload: dict):
        return self.repo.create_from_dict(payload)

    def update_category(self, category_id: int, payload: dict):
        db_cat = self.repo.get_by_id(category_id)
        if not db_cat:
            raise HTTPException(status_code=404, detail="Category not found")
        return self.repo.update_fields(db_cat, payload)

    def delete_category(self, category_id: int):
        db_cat = self.repo.get_by_id(category_id)
        if not db_cat:
            raise HTTPException(status_code=404, detail="Category not found")
        self.repo.db.delete(db_cat)
        self.repo.db.commit()
        return {"ok": True}
