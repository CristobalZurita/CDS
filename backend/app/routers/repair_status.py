from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.dependencies import require_permission
from app.models.repair import RepairStatus
from app.schemas.repair_status import (
    OkResponse,
    RepairStatusCreate,
    RepairStatusCreatedResponse,
    RepairStatusRead,
    RepairStatusUpdate,
)

router = APIRouter(prefix="/repair-statuses", tags=["repair-statuses"])


@router.get("/", response_model=List[RepairStatusRead])
def list_statuses(db: Session = Depends(get_db)):
    statuses = db.query(RepairStatus).order_by(RepairStatus.sort_order).all()
    return [{"id": s.id, "code": s.code, "name": s.name, "color": s.color} for s in statuses]


@router.post("/", response_model=RepairStatusCreatedResponse, status_code=status.HTTP_201_CREATED)
def create_status(
    payload: RepairStatusCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repair_statuses", "create"))
):
    status_row = RepairStatus(
        code=payload.code,
        name=payload.name,
        description=payload.description,
        color=payload.color,
        sort_order=payload.sort_order,
    )
    db.add(status_row)
    db.commit()
    db.refresh(status_row)
    return {"id": status_row.id}


@router.put("/{status_id}", response_model=OkResponse)
def update_status(
    status_id: int,
    payload: RepairStatusUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repair_statuses", "update"))
):
    status_row = db.query(RepairStatus).filter(RepairStatus.id == status_id).first()
    if not status_row:
        raise HTTPException(status_code=404, detail="Status not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        if hasattr(status_row, key):
            setattr(status_row, key, value)
    db.commit()
    db.refresh(status_row)
    return {"ok": True}


@router.delete("/{status_id}", response_model=OkResponse)
def delete_status(status_id: int, db: Session = Depends(get_db), user: dict = Depends(require_permission("repair_statuses", "delete"))):
    status_row = db.query(RepairStatus).filter(RepairStatus.id == status_id).first()
    if not status_row:
        raise HTTPException(status_code=404, detail="Status not found")
    db.delete(status_row)
    db.commit()
    return {"ok": True}
