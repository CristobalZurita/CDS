from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.instrument import Instrument
from app.core.database import get_db
from app.core.dependencies import require_permission
from app.schemas.instrument import InstrumentCreate, InstrumentRead, InstrumentUpdate, OkResponse

router = APIRouter(prefix="/instruments", tags=["Instruments"])

@router.get("/", response_model=List[InstrumentRead])
def list_instruments(db: Session = Depends(get_db)):
    return db.query(Instrument).all()

@router.post("/", response_model=InstrumentRead, status_code=status.HTTP_201_CREATED)
def create_instrument(
    payload: InstrumentCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("instruments", "create"))
):
    db_inst = Instrument(**payload.model_dump())
    db.add(db_inst)
    db.commit()
    db.refresh(db_inst)
    return db_inst

@router.put("/{instrument_id}", response_model=InstrumentRead)
def update_instrument(
    instrument_id: int,
    payload: InstrumentUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("instruments", "update"))
):
    db_inst = db.get(Instrument, instrument_id)
    if not db_inst:
        raise HTTPException(status_code=404, detail="Instrument not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(db_inst, k, v)
    db.commit()
    db.refresh(db_inst)
    return db_inst

@router.delete("/{instrument_id}", response_model=OkResponse)
def delete_instrument(instrument_id: int, db: Session = Depends(get_db), user: dict = Depends(require_permission("instruments", "delete"))):
    db_inst = db.get(Instrument, instrument_id)
    if not db_inst:
        raise HTTPException(status_code=404, detail="Instrument not found")
    db.delete(db_inst)
    db.commit()
    return {"ok": True}
