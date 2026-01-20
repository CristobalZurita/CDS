from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict

from app.core.database import get_db
from app.core.dependencies import get_current_admin, require_permission
from app.models.repair import RepairStatus

router = APIRouter(prefix="/repair-statuses", tags=["repair-statuses"])


@router.get("/", response_model=List[Dict])
def list_statuses(db: Session = Depends(get_db)):
    statuses = db.query(RepairStatus).order_by(RepairStatus.sort_order).all()
    return [{"id": s.id, "code": s.code, "name": s.name, "color": s.color} for s in statuses]


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_status(payload: Dict, db: Session = Depends(get_db), user: dict = Depends(require_permission("repair_statuses", "create"))):
    if not payload.get("code") or not payload.get("name"):
        raise HTTPException(status_code=400, detail="code and name required")
    status_row = RepairStatus(
        code=payload.get("code"),
        name=payload.get("name"),
        description=payload.get("description"),
        color=payload.get("color"),
        sort_order=payload.get("sort_order", 0),
    )
    db.add(status_row)
    db.commit()
    db.refresh(status_row)
    return {"id": status_row.id}


@router.put("/{status_id}")
def update_status(status_id: int, payload: Dict, db: Session = Depends(get_db), user: dict = Depends(require_permission("repair_statuses", "update"))):
    status_row = db.query(RepairStatus).filter(RepairStatus.id == status_id).first()
    if not status_row:
        raise HTTPException(status_code=404, detail="Status not found")
    for key, value in payload.items():
        if hasattr(status_row, key):
            setattr(status_row, key, value)
    db.commit()
    db.refresh(status_row)
    return {"ok": True}


@router.delete("/{status_id}")
def delete_status(status_id: int, db: Session = Depends(get_db), user: dict = Depends(require_permission("repair_statuses", "delete"))):
    status_row = db.query(RepairStatus).filter(RepairStatus.id == status_id).first()
    if not status_row:
        raise HTTPException(status_code=404, detail="Status not found")
    db.delete(status_row)
    db.commit()
    return {"ok": True}
