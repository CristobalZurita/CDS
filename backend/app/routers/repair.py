from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.repair import Repair
from typing import Dict
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.services.logging_service import create_audit
from app.services.repair_service import RepairService
from app.models.repair_note import RepairNote
from app.models.repair_photo import RepairPhoto

router = APIRouter(prefix="/repairs", tags=["repairs"])


@router.get("/")
def list_repairs(db: Session = Depends(get_db)):
    return db.query(Repair).all()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_repair(repair: Dict, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    # Accept a flexible payload for now to avoid schema package conflicts
    db_repair = Repair(**repair)
    db.add(db_repair)
    db.commit()
    db.refresh(db_repair)
    # Audit: repair created
    try:
        create_audit(event_type="repair.create", user_id=None, details={"repair_id": db_repair.id}, message="Repair created")
    except Exception:
        # Non-fatal: auditing should not break main flow
        pass
    return db_repair


@router.put("/{repair_id}")
def update_repair(repair_id: int, repair: Dict, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
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
def delete_repair(repair_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
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


# ---------------------------------------------------------------------------
# Endpoints that use RepairService for transactional operations
# ---------------------------------------------------------------------------


@router.post("/{repair_id}/components", status_code=status.HTTP_201_CREATED)
def add_component_usage(repair_id: int, payload: Dict, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    """Registrar uso de un componente en una reparación y descontar stock"""
    required = ("component_table", "component_id", "quantity")
    for k in required:
        if k not in payload:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Missing field: {k}")

    svc = RepairService(db)
    try:
        usage = svc.add_component_usage(
            repair_id=repair_id,
            component_table=str(payload["component_table"]),
            component_id=int(payload["component_id"]),
            quantity=int(payload["quantity"]),
            user_id=int(user.get("user_id")) if user and user.get("user_id") else None,
            notes=payload.get("notes")
        )
        return usage
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{repair_id}/components")
def list_component_usages(repair_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    svc = RepairService(db)
    return svc.get_component_usages(repair_id)


@router.post("/{repair_id}/notes", status_code=status.HTTP_201_CREATED)
def add_repair_note(repair_id: int, payload: Dict, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    """Agregar nota técnica o interna a una reparación"""
    note_text = payload.get("note")
    if not note_text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing field: note")

    note = RepairNote(
        repair_id=repair_id,
        user_id=int(user.get("user_id")) if user and user.get("user_id") else None,
        note=note_text,
        note_type=payload.get("note_type", "internal")
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.post("/{repair_id}/photos", status_code=status.HTTP_201_CREATED)
def add_repair_photo(repair_id: int, payload: Dict, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    """Registrar URL de foto asociada a la reparación. For file uploads use `uploads` router."""
    photo_url = payload.get("photo_url")
    if not photo_url:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing field: photo_url")

    photo = RepairPhoto(
        repair_id=repair_id,
        photo_url=photo_url,
        photo_type=payload.get("photo_type", "general"),
        caption=payload.get("caption")
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo
