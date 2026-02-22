"""
Repositorio de Category (aditivo, no destructivo).
Centraliza acceso de datos para categories sin cambiar contratos existentes.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models.category import Category

from .base_repository import BaseRepository


class CategoryRepository(BaseRepository[Category, dict, dict]):
    def __init__(self, db: Session):
        super().__init__(Category, db)

    def list_all(self) -> list[Category]:
        return self.db.query(Category).all()

    def get_existing_by_name(self, name: str) -> Optional[Category]:
        return self.db.query(Category).filter(Category.name == name).first()
