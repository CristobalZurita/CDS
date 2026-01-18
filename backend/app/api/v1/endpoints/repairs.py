"""Repair endpoints (API v1)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.repair import RepairCreate, RepairUpdate, RepairRead
from app.crud.repair import create_repair, list_repairs, get_repair, update_repair, delete_repair

router = APIRouter(prefix="/repairs", tags=["repairs"])


@router.get("/", response_model=List[RepairRead])
def list_repairs_endpoint(db: Session = Depends(get_db)):
    return list_repairs(db)


@router.get("/{repair_id}", response_model=RepairRead)
def get_repair_endpoint(repair_id: int, db: Session = Depends(get_db)):
    repair = get_repair(db, repair_id)
    if not repair:
        raise HTTPException(status_code=404, detail="Repair not found")
    return repair


@router.post("/", response_model=RepairRead, status_code=status.HTTP_201_CREATED)
def create_repair_endpoint(payload: RepairCreate, db: Session = Depends(get_db)):
    return create_repair(db, payload)


@router.put("/{repair_id}", response_model=RepairRead)
def update_repair_endpoint(repair_id: int, payload: RepairUpdate, db: Session = Depends(get_db)):
    repair = update_repair(db, repair_id, payload)
    if not repair:
        raise HTTPException(status_code=404, detail="Repair not found")
    return repair


@router.delete("/{repair_id}")
def delete_repair_endpoint(repair_id: int, db: Session = Depends(get_db)):
    ok = delete_repair(db, repair_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Repair not found")
    return {"ok": True}
