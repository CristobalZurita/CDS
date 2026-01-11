from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.models.instrument import Instrument
from backend.app.core.database import get_db

router = APIRouter(prefix="/api/instruments", tags=["Instruments"])

@router.get("/")
def list_instruments(db: Session = Depends(get_db)):
    return db.query(Instrument).all()

@router.post("/")
def create_instrument(payload: dict, db: Session = Depends(get_db)):
    db_inst = Instrument(**payload)
    db.add(db_inst)
    db.commit()
    db.refresh(db_inst)
    return db_inst

@router.put("/{instrument_id}")
def update_instrument(instrument_id: int, payload: dict, db: Session = Depends(get_db)):
    db_inst = db.query(Instrument).get(instrument_id)
    if not db_inst:
        raise HTTPException(status_code=404, detail="Instrument not found")
    for k, v in payload.items():
        setattr(db_inst, k, v)
    db.commit()
    db.refresh(db_inst)
    return db_inst

@router.delete("/{instrument_id}")
def delete_instrument(instrument_id: int, db: Session = Depends(get_db)):
    db_inst = db.query(Instrument).get(instrument_id)
    if not db_inst:
        raise HTTPException(status_code=404, detail="Instrument not found")
    db.delete(db_inst)
    db.commit()
    return {"ok": True}
