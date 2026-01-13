"""
CRUD operations para diagnósticos
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from backend.app.crud.base import CRUDBase
from backend.app.models.diagnostic import Diagnostic
from backend.app.schemas.diagnostic import DiagnosticCreate, DiagnosticUpdate


class CRUDDiagnostic(CRUDBase[Diagnostic, DiagnosticCreate, DiagnosticUpdate]):
    """CRUD operations para diagnósticos"""

    def get_by_repair(
        self,
        db: Session,
        repair_id: int
    ) -> Optional[Diagnostic]:
        """Obtiene diagnóstico asociado a una reparación"""
        return (
            db.query(self.model)
            .filter(self.model.repair_id == repair_id)
            .first()
        )

    def get_by_confidence(
        self,
        db: Session,
        min_confidence: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Diagnostic]:
        """Obtiene diagnósticos filtrados por confianza mínima de IA"""
        return (
            db.query(self.model)
            .filter(self.model.ai_confidence >= min_confidence)
            .order_by(self.model.ai_confidence.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_with_quotes(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Diagnostic]:
        """Obtiene diagnósticos que tienen cotización generada"""
        return (
            db.query(self.model)
            .filter(self.model.quote_total.isnot(None))
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_quote(
        self,
        db: Session,
        diagnostic_id: int,
        quote_total: int,
        quote_breakdown: dict,
        labor_hours: Optional[int] = None
    ) -> Optional[Diagnostic]:
        """
        Actualiza la cotización de un diagnóstico
        """
        diagnostic = self.get(db, diagnostic_id)
        if not diagnostic:
            return None

        diagnostic.quote_total = quote_total
        diagnostic.quote_breakdown = quote_breakdown
        if labor_hours is not None:
            diagnostic.labor_hours = labor_hours
        diagnostic.updated_at = datetime.utcnow()

        db.add(diagnostic)
        db.commit()
        db.refresh(diagnostic)
        return diagnostic

    def update_ai_analysis(
        self,
        db: Session,
        diagnostic_id: int,
        ai_analysis: dict,
        detected_faults: List[dict],
        ai_confidence: int
    ) -> Optional[Diagnostic]:
        """
        Actualiza el análisis de IA de un diagnóstico
        """
        diagnostic = self.get(db, diagnostic_id)
        if not diagnostic:
            return None

        diagnostic.ai_analysis = ai_analysis
        diagnostic.detected_faults = detected_faults
        diagnostic.ai_confidence = ai_confidence
        diagnostic.updated_at = datetime.utcnow()

        db.add(diagnostic)
        db.commit()
        db.refresh(diagnostic)
        return diagnostic

    def add_note(
        self,
        db: Session,
        diagnostic_id: int,
        note_text: str
    ) -> Optional[Diagnostic]:
        """Agrega una nota a un diagnóstico"""
        diagnostic = self.get(db, diagnostic_id)
        if not diagnostic:
            return None

        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        new_note = f"[{timestamp}] {note_text}"

        if diagnostic.notes:
            diagnostic.notes = f"{diagnostic.notes}\n{new_note}"
        else:
            diagnostic.notes = new_note

        diagnostic.updated_at = datetime.utcnow()

        db.add(diagnostic)
        db.commit()
        db.refresh(diagnostic)
        return diagnostic


# Instancia singleton
diagnostic = CRUDDiagnostic(Diagnostic)
