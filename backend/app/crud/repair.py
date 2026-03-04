"""CRUD for Repair."""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.repair import Repair
from app.schemas.repair import RepairCreate, RepairUpdate


def create_repair(db: Session, payload: RepairCreate) -> Repair:
    data = payload.model_dump()
    repair = Repair(**data)
    db.add(repair)
    db.commit()
    db.refresh(repair)
    return repair


def get_repair(db: Session, repair_id: int) -> Optional[Repair]:
    return db.query(Repair).filter(Repair.id == repair_id).first()


def list_repairs(db: Session, skip: int = 0, limit: int = 100) -> List[Repair]:
    return db.query(Repair).offset(skip).limit(limit).all()


def update_repair(db: Session, repair_id: int, payload: RepairUpdate) -> Optional[Repair]:
    repair = get_repair(db, repair_id)
    if not repair:
        return None
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(repair, key, value)
    db.commit()
    db.refresh(repair)
    return repair


def delete_repair(db: Session, repair_id: int) -> bool:
    repair = get_repair(db, repair_id)
    if not repair:
        return False
    db.delete(repair)
    db.commit()
    return True
