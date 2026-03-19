from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.repair import Repair
from app.services.repair_state_machine import RepairStateID


def get_repair_or_404(db: Session, repair_id: int) -> Repair:
    repair = db.query(Repair).filter(Repair.id == repair_id).first()
    if not repair:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reparación {repair_id} no encontrada",
        )
    return repair


def is_repair_closed(repair: Repair) -> bool:
    if repair.status_obj:
        return repair.status_obj.code in ("archivado", "rechazado")
    return repair.status_id in (RepairStateID.ARCHIVADO, RepairStateID.RECHAZADO)


def recalculate_parts_cost(repair: Repair) -> None:
    total = 0.0
    for usage in repair.component_usages:
        if usage.unit_cost:
            total += usage.quantity * usage.unit_cost
    repair.parts_cost = total
    repair.total_cost = (
        (repair.parts_cost or 0)
        + (repair.labor_cost or 0)
        + (repair.additional_cost or 0)
        - (repair.discount or 0)
    )
