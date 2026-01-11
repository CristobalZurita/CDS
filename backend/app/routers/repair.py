from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.models.repair import Repair
from typing import Dict
from backend.app.core.database import get_db
from backend.app.services.logging_service import create_audit

router = APIRouter(prefix="/repairs", tags=["Repairs"])

@router.get("/")
def list_repairs(db: Session = Depends(get_db)):
    return db.query(Repair).all()

@router.post("/")
def create_repair(repair: Dict, db: Session = Depends(get_db)):
    # Accept a flexible payload for now to avoid schema package conflicts
    db_repair = Repair(**repair)
    db.add(db_repair)
    db.commit()
    db.refresh(db_repair)
    # Audit: repair created
    try:
        # Keep audit payload minimal and defensive: avoid referencing optional attrs
        create_audit(event_type="repair.create", user_id=None, details={"repair_id": db_repair.id}, message="Repair created")
    except Exception:
        # Non-fatal: auditing should not break main flow
        pass
    return db_repair

@router.put("/{repair_id}")
def update_repair(repair_id: int, repair: Dict, db: Session = Depends(get_db)):
    db_repair = db.query(Repair).get(repair_id)
    if not db_repair:
        raise HTTPException(status_code=404, detail="Repair not found")
    for key, value in repair.items():
        setattr(db_repair, key, value)
    db.commit()
    db.refresh(db_repair)
    # Audit: repair updated
    try:
        create_audit(event_type="repair.update", user_id=None, details={"repair_id": db_repair.id}, message="Repair updated")
    except Exception:
        pass
    return db_repair

@router.delete("/{repair_id}")
def delete_repair(repair_id: int, db: Session = Depends(get_db)):
    db_repair = db.query(Repair).get(repair_id)
    if not db_repair:
        raise HTTPException(status_code=404, detail="Repair not found")
    db.delete(db_repair)
    db.commit()
    # Audit: repair deleted
    try:
        create_audit(event_type="repair.delete", user_id=None, details={"repair_id": repair_id}, message="Repair deleted")
    except Exception:
        pass
    return {"ok": True}
