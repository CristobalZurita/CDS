"""
Repositorio de Repair (aditivo, no destructivo).
Extiende BaseRepository y concentra queries frecuentes de OT/Repair.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models.repair import Repair
from app.schemas.repair import RepairCreate, RepairUpdate

from .base_repository import BaseRepository


class RepairRepository(BaseRepository[Repair, RepairCreate, RepairUpdate]):
    def __init__(self, db: Session):
        super().__init__(Repair, db)

    def list_active(self):
        return self.db.query(Repair).filter(Repair.archived_at.is_(None)).all()

    def list_archived(self):
        return self.db.query(Repair).filter(Repair.archived_at.isnot(None)).all()

    def get_last_created(self) -> Optional[Repair]:
        return self.db.query(Repair).order_by(Repair.id.desc()).first()

    def get_by_repair_number(self, repair_number: str) -> Optional[Repair]:
        return (
            self.db.query(Repair)
            .filter(Repair.repair_number == repair_number)
            .first()
        )
