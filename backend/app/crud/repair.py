"""
CRUD operations para reparaciones
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from backend.app.crud.base import CRUDBase
from backend.app.models.repair import Repair, RepairStatus
from backend.app.schemas.repair import RepairCreate, RepairUpdate


class CRUDRepair(CRUDBase[Repair, RepairCreate, RepairUpdate]):
    """CRUD operations para reparaciones"""

    def get_by_client(
        self,
        db: Session,
        client_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Repair]:
        """Obtiene todas las reparaciones de un cliente"""
        return (
            db.query(self.model)
            .filter(self.model.client_id == client_id)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_status(
        self,
        db: Session,
        status: RepairStatus,
        skip: int = 0,
        limit: int = 100
    ) -> List[Repair]:
        """Obtiene reparaciones filtradas por estado"""
        return (
            db.query(self.model)
            .filter(self.model.status == status)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_active(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Repair]:
        """Obtiene reparaciones activas (no canceladas ni entregadas)"""
        active_statuses = [
            RepairStatus.PENDING,
            RepairStatus.IN_PROGRESS,
            RepairStatus.WAITING_PARTS,
            RepairStatus.COMPLETED,
            RepairStatus.READY_PICKUP,
        ]
        return (
            db.query(self.model)
            .filter(self.model.status.in_(active_statuses))
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_status(
        self,
        db: Session,
        repair_id: int,
        new_status: RepairStatus,
        notes: Optional[str] = None
    ) -> Optional[Repair]:
        """
        Actualiza el estado de una reparación y ajusta timestamps
        """
        repair = self.get(db, repair_id)
        if not repair:
            return None

        # Actualizar estado
        repair.status = new_status

        # Actualizar timestamps según estado
        if new_status == RepairStatus.IN_PROGRESS and not repair.started_at:
            repair.started_at = datetime.utcnow()

        elif new_status in [RepairStatus.COMPLETED, RepairStatus.READY_PICKUP]:
            if not repair.completed_at:
                repair.completed_at = datetime.utcnow()

        # Agregar nota si se proporcionó
        if notes:
            self._append_note(repair, notes)

        # Actualizar updated_at
        repair.updated_at = datetime.utcnow()

        db.add(repair)
        db.commit()
        db.refresh(repair)
        return repair

    def add_note(
        self,
        db: Session,
        repair_id: int,
        note_text: str
    ) -> Optional[Repair]:
        """Agrega una nota a una reparación"""
        repair = self.get(db, repair_id)
        if not repair:
            return None

        self._append_note(repair, note_text)
        repair.updated_at = datetime.utcnow()

        db.add(repair)
        db.commit()
        db.refresh(repair)
        return repair

    def _append_note(self, repair: Repair, note_text: str) -> None:
        """Helper privado para agregar nota con timestamp"""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        new_note = f"[{timestamp}] {note_text}"

        if repair.notes:
            repair.notes = f"{repair.notes}\n{new_note}"
        else:
            repair.notes = new_note

    def get_stats(self, db: Session) -> dict:
        """Obtiene estadísticas de reparaciones por estado"""
        total = db.query(self.model).count()

        stats = {
            "total": total,
            "pending": db.query(self.model).filter(self.model.status == RepairStatus.PENDING).count(),
            "in_progress": db.query(self.model).filter(self.model.status == RepairStatus.IN_PROGRESS).count(),
            "waiting_parts": db.query(self.model).filter(self.model.status == RepairStatus.WAITING_PARTS).count(),
            "completed": db.query(self.model).filter(self.model.status == RepairStatus.COMPLETED).count(),
            "ready_pickup": db.query(self.model).filter(self.model.status == RepairStatus.READY_PICKUP).count(),
            "delivered": db.query(self.model).filter(self.model.status == RepairStatus.DELIVERED).count(),
            "cancelled": db.query(self.model).filter(self.model.status == RepairStatus.CANCELLED).count(),
        }

        return stats


# Instancia singleton
repair = CRUDRepair(Repair)
