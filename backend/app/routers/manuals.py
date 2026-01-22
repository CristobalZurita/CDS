from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path
import os

from app.core.database import get_db
from app.core.dependencies import require_permission
from app.models.manual_document import ManualDocument
from app.models.instrument import Instrument
from app.schemas.manual import ManualCreate, ManualOut

router = APIRouter(prefix="/manuals", tags=["manuals"])


def _save_manual(file: UploadFile, dest_dir: str) -> str:
    Path(dest_dir).mkdir(parents=True, exist_ok=True)
    safe_name = Path(file.filename).name
    dest = Path(dest_dir) / safe_name
    with open(dest, "wb") as f:
        while True:
            chunk = file.file.read(1024 * 64)
            if not chunk:
                break
            f.write(chunk)
    return str(dest)


@router.get("/", response_model=List[ManualOut])
def list_manuals(
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("manuals", "read")),
):
    return db.query(ManualDocument).order_by(ManualDocument.created_at.desc()).all()


@router.post("/", response_model=ManualOut, status_code=201)
def create_manual(
    payload: ManualCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("manuals", "create")),
):
    instrument = db.query(Instrument).filter(Instrument.id == payload.instrument_id).first()
    if not instrument:
        raise HTTPException(status_code=404, detail="Instrument not found")
    manual = ManualDocument(
        instrument_id=payload.instrument_id,
        title=payload.title.strip(),
        source=payload.source or "internal",
        url=payload.url,
        file_path=payload.file_path,
    )
    db.add(manual)
    db.commit()
    db.refresh(manual)
    return manual


@router.post("/upload/{instrument_id}", response_model=ManualOut, status_code=201)
def upload_manual(
    instrument_id: int,
    title: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("manuals", "create")),
):
    instrument = db.query(Instrument).filter(Instrument.id == instrument_id).first()
    if not instrument:
        raise HTTPException(status_code=404, detail="Instrument not found")
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in (".pdf", ".png", ".jpg", ".jpeg"):
        raise HTTPException(status_code=400, detail="Invalid file type")
    path = _save_manual(file, os.path.join("uploads", "manuals", f"instrument-{instrument_id}"))
    manual = ManualDocument(
        instrument_id=instrument_id,
        title=title.strip(),
        source="internal",
        file_path=path,
    )
    db.add(manual)
    db.commit()
    db.refresh(manual)
    return manual
