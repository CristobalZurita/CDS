"""
Base repository (aditivo) sobre CRUDBase existente.
No reemplaza routers/crud actuales; solo agrega capa reusable.
"""

from __future__ import annotations

from typing import Any, Dict, Generic, Optional, Type, TypeVar

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase


ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Repositorio base reutilizable para modelos SQLAlchemy."""

    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db
        self._crud = CRUDBase(model)

    def get_by_id(self, item_id: int) -> Optional[ModelType]:
        return self._crud.get(self.db, item_id)

    def get_all(self, skip: int = 0, limit: int = 100):
        return self._crud.get_all(self.db, skip=skip, limit=limit)

    def create(self, payload: CreateSchemaType) -> ModelType:
        return self._crud.create(self.db, payload)

    def create_from_dict(self, payload: Dict[str, Any]) -> ModelType:
        item = self.model(**payload)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update(self, db_obj: ModelType, payload: UpdateSchemaType) -> ModelType:
        return self._crud.update(self.db, db_obj, payload)

    def update_fields(self, db_obj: ModelType, fields: Dict[str, Any]) -> ModelType:
        for key, value in fields.items():
            setattr(db_obj, key, value)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete_by_id(self, item_id: int) -> bool:
        return self._crud.delete_by_id(self.db, item_id)
