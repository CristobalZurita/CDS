"""Diagnostic endpoints (API v1)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.diagnostic import Diagnostic
from app.schemas.diagnostic import DiagnosticCreate, DiagnosticUpdate, DiagnosticRead

router = APIRouter(prefix="/diagnostics", tags=["diagnostics"])


@router.get("/", response_model=List[DiagnosticRead])
def list_diagnostics(db: Session = Depends(get_db)):
    return db.query(Diagnostic).all()


@router.get("/{diagnostic_id}", response_model=DiagnosticRead)
def get_diagnostic(diagnostic_id: int, db: Session = Depends(get_db)):
    diagnostic = db.query(Diagnostic).filter(Diagnostic.id == diagnostic_id).first()
    if not diagnostic:
        raise HTTPException(status_code=404, detail="Diagnostic not found")
    return diagnostic


@router.post("/", response_model=DiagnosticRead, status_code=status.HTTP_201_CREATED)
def create_diagnostic(payload: DiagnosticCreate, db: Session = Depends(get_db)):
    diagnostic = Diagnostic(**payload.dict())
    db.add(diagnostic)
    db.commit()
    db.refresh(diagnostic)
    return diagnostic


@router.put("/{diagnostic_id}", response_model=DiagnosticRead)
def update_diagnostic(diagnostic_id: int, payload: DiagnosticUpdate, db: Session = Depends(get_db)):
    diagnostic = db.query(Diagnostic).filter(Diagnostic.id == diagnostic_id).first()
    if not diagnostic:
        raise HTTPException(status_code=404, detail="Diagnostic not found")
    data = payload.dict(exclude_unset=True)
    for key, value in data.items():
        setattr(diagnostic, key, value)
    db.commit()
    db.refresh(diagnostic)
    return diagnostic


@router.delete("/{diagnostic_id}")
def delete_diagnostic(diagnostic_id: int, db: Session = Depends(get_db)):
    diagnostic = db.query(Diagnostic).filter(Diagnostic.id == diagnostic_id).first()
    if not diagnostic:
        raise HTTPException(status_code=404, detail="Diagnostic not found")
    db.delete(diagnostic)
    db.commit()
    return {"ok": True}
