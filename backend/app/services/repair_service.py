"""
Servicio fachada para dominio Repair.
Mantiene el contrato existente y delega la lógica a servicios internos por subdominio.
"""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.repair import Repair
from app.models.repair_component_usage import RepairComponentUsage
from app.services.repair_component_stock_service import RepairComponentStockService
from app.services.repair_service_support import get_repair_or_404, is_repair_closed
from app.services.repair_status_flow_service import RepairStatusFlowService


class RepairService:
    """Fachada estable para operaciones transaccionales del dominio Repair."""

    def __init__(self, db: Session):
        self.db = db
        self.component_service = RepairComponentStockService(db)
        self.status_service = RepairStatusFlowService(db)

    def get_repair(self, repair_id: int) -> Repair:
        return get_repair_or_404(self.db, repair_id)

    def is_repair_closed(self, repair: Repair) -> bool:
        return is_repair_closed(repair)

    def add_component_usage(
        self,
        repair_id: int,
        component_table: str,
        component_id: int,
        quantity: int,
        user_id: Optional[int],
        from_reserved: bool = False,
        notes: Optional[str] = None,
    ) -> RepairComponentUsage:
        return self.component_service.add_component_usage(
            repair_id=repair_id,
            component_table=component_table,
            component_id=component_id,
            quantity=quantity,
            user_id=user_id,
            from_reserved=from_reserved,
            notes=notes,
        )

    def reserve_component(
        self,
        repair_id: int,
        component_table: str,
        component_id: int,
        quantity: int,
        user_id: Optional[int],
        notes: Optional[str] = None,
    ) -> dict:
        return self.component_service.reserve_component(
            repair_id=repair_id,
            component_table=component_table,
            component_id=component_id,
            quantity=quantity,
            user_id=user_id,
            notes=notes,
        )

    def release_component_reservation(
        self,
        repair_id: int,
        component_table: str,
        component_id: int,
        quantity: int,
        user_id: Optional[int],
        notes: Optional[str] = None,
    ) -> dict:
        return self.component_service.release_component_reservation(
            repair_id=repair_id,
            component_table=component_table,
            component_id=component_id,
            quantity=quantity,
            user_id=user_id,
            notes=notes,
        )

    def remove_component_usage(
        self,
        usage_id: int,
        user_id: Optional[int],
    ) -> dict:
        return self.component_service.remove_component_usage(
            usage_id=usage_id,
            user_id=user_id,
        )

    def update_labor_cost(self, repair_id: int, labor_cost: float) -> Repair:
        return self.component_service.update_labor_cost(repair_id, labor_cost)

    def close_repair(self, repair_id: int, user_id: int) -> Repair:
        return self.status_service.close_repair(repair_id, user_id)

    def get_component_usages(self, repair_id: int) -> List[RepairComponentUsage]:
        return self.component_service.get_component_usages(repair_id)

    def get_repair_economic_summary(self, repair_id: int) -> dict:
        return self.component_service.get_repair_economic_summary(repair_id)

    def update_status(
        self,
        repair_id: int,
        new_status_id: int,
        user_id: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> Repair:
        return self.status_service.update_status(
            repair_id=repair_id,
            new_status_id=new_status_id,
            user_id=user_id,
            notes=notes,
        )
