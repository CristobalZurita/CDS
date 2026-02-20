"""
Servicio de lectura para Repair/OT (aditivo).
Encapsula consultas de lectura usando RepairRepository.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models.repair import Repair
from app.repositories.repair_repository import RepairRepository


class RepairReadService:
    """Capa de lectura (query) para OT."""

    def __init__(self, db: Session):
        self.repo = RepairRepository(db)

    def list_active(self):
        return self.repo.list_active()

    def list_archived(self):
        return self.repo.list_archived()

    def get_by_id(self, repair_id: int) -> Optional[Repair]:
        return self.repo.get_by_id(repair_id)

    def get_last_created(self) -> Optional[Repair]:
        return self.repo.get_last_created()
