"""
CRUD operations para cotizaciones
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from backend.app.crud.base import CRUDBase
from backend.app.models.quote import Quote, QuoteStatus
from backend.app.schemas.quote import QuoteCreate, QuoteUpdate


class CRUDQuote(CRUDBase[Quote, QuoteCreate, QuoteUpdate]):
    """CRUD operations para cotizaciones"""

    def get_by_diagnostic(
        self,
        db: Session,
        diagnostic_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Quote]:
        """Obtiene cotizaciones de un diagnóstico"""
        return (
            db.query(self.model)
            .filter(self.model.diagnostic_id == diagnostic_id)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_repair(
        self,
        db: Session,
        repair_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Quote]:
        """Obtiene cotizaciones de una reparación"""
        return (
            db.query(self.model)
            .filter(self.model.repair_id == repair_id)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_status(
        self,
        db: Session,
        status: QuoteStatus,
        skip: int = 0,
        limit: int = 100
    ) -> List[Quote]:
        """Obtiene cotizaciones por estado"""
        return (
            db.query(self.model)
            .filter(self.model.status == status)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_pending(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Quote]:
        """Obtiene cotizaciones pendientes"""
        return self.get_by_status(db, QuoteStatus.PENDING, skip, limit)

    def get_accepted(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Quote]:
        """Obtiene cotizaciones aceptadas"""
        return self.get_by_status(db, QuoteStatus.ACCEPTED, skip, limit)

    def get_expired(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Quote]:
        """Obtiene cotizaciones que deberían estar expiradas"""
        return (
            db.query(self.model)
            .filter(self.model.status == QuoteStatus.SENT)
            .filter(
                self.model.created_at + timedelta(days=self.model.validity_days) < datetime.utcnow()
            )
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_status(
        self,
        db: Session,
        quote_id: int,
        new_status: QuoteStatus,
        notes: Optional[str] = None
    ) -> Optional[Quote]:
        """
        Actualiza el estado de una cotización
        """
        quote = self.get(db, quote_id)
        if not quote:
            return None

        quote.status = new_status
        if notes:
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            new_note = f"[{timestamp}] {notes}"
            if quote.notes:
                quote.notes = f"{quote.notes}\n{new_note}"
            else:
                quote.notes = new_note

        quote.updated_at = datetime.utcnow()

        db.add(quote)
        db.commit()
        db.refresh(quote)
        return quote

    def mark_as_sent(
        self,
        db: Session,
        quote_id: int
    ) -> Optional[Quote]:
        """Marca una cotización como enviada"""
        return self.update_status(db, quote_id, QuoteStatus.SENT, "Cotización enviada")

    def mark_as_accepted(
        self,
        db: Session,
        quote_id: int
    ) -> Optional[Quote]:
        """Marca una cotización como aceptada"""
        return self.update_status(db, quote_id, QuoteStatus.ACCEPTED, "Cotización aceptada por el cliente")

    def mark_as_rejected(
        self,
        db: Session,
        quote_id: int
    ) -> Optional[Quote]:
        """Marca una cotización como rechazada"""
        return self.update_status(db, quote_id, QuoteStatus.REJECTED, "Cotización rechazada por el cliente")

    def mark_as_expired(
        self,
        db: Session,
        quote_id: int
    ) -> Optional[Quote]:
        """Marca una cotización como expirada"""
        return self.update_status(db, quote_id, QuoteStatus.EXPIRED, "Cotización expirada")

    def get_stats(self, db: Session) -> dict:
        """Obtiene estadísticas de cotizaciones"""
        total = db.query(self.model).count()

        stats = {
            "total": total,
            "pending": db.query(self.model).filter(self.model.status == QuoteStatus.PENDING).count(),
            "sent": db.query(self.model).filter(self.model.status == QuoteStatus.SENT).count(),
            "accepted": db.query(self.model).filter(self.model.status == QuoteStatus.ACCEPTED).count(),
            "rejected": db.query(self.model).filter(self.model.status == QuoteStatus.REJECTED).count(),
            "expired": db.query(self.model).filter(self.model.status == QuoteStatus.EXPIRED).count(),
        }

        return stats


# Instancia singleton
quote = CRUDQuote(Quote)
