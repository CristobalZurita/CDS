from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.stock_movement import StockMovement
from app.core.database import get_db
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/stock-movements", tags=["StockMovements"])

@router.get("/")
def list_movements(db: Session = Depends(get_db)):
    return db.query(StockMovement).all()

@router.post("/")
def create_movement(payload: dict, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    db_obj = StockMovement(**payload)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
