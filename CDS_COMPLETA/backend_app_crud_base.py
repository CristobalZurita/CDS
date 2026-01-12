"""
Generic CRUD operations base class
Provides common Create, Read, Update, Delete operations
"""

from typing import TypeVar, Generic, Type, List, Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Type variables for generic ORM model and schema
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Generic CRUD base class
    Usage: class CRUDInstrument(CRUDBase[Instrument, InstrumentCreate, InstrumentUpdate]):
    """

    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: any) -> Optional[ModelType]:
        """Get single record by ID"""
        return db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all records with pagination"""
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        """Create new record"""
        obj_data = obj_in.dict()
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        """Update existing record"""
        obj_data = obj_in.dict(exclude_unset=True)
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: any) -> Optional[ModelType]:
        """Delete record by ID"""
        db_obj = db.query(self.model).filter(self.model.id == id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj

    def delete_by_id(self, db: Session, id: any) -> bool:
        """Delete record and return success status"""
        result = db.query(self.model).filter(self.model.id == id).delete()
        db.commit()
        return result > 0
