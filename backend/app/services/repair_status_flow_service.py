from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.repair import Repair, RepairStatus
from app.models.repair_note import RepairNote
from app.services.event_system import Events, event_bus
from app.services.logging_service import create_audit
from app.services.repair_service_support import get_repair_or_404, is_repair_closed
from app.services.repair_state_machine import (
    RepairStateID,
    get_state_name,
    get_state_progress,
    validate_transition,
)


class RepairStatusFlowService:
    def __init__(self, db: Session):
        self.db = db

    def close_repair(self, repair_id: int, user_id: int) -> Repair:
        repair = get_repair_or_404(self.db, repair_id)
        if is_repair_closed(repair):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reparación ya está cerrada",
            )

        delivered_status = (
            self.db.query(RepairStatus)
            .filter(RepairStatus.code == "delivered")
            .first()
        )
        repair.status_id = delivered_status.id if delivered_status else 4
        repair.delivery_date = datetime.utcnow()
        repair.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(repair)
        return repair

    def update_status(
        self,
        repair_id: int,
        new_status_id: int,
        user_id: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> Repair:
        repair = get_repair_or_404(self.db, repair_id)
        current_status_id = repair.status_id
        if current_status_id == new_status_id:
            return repair

        validate_transition(current_status_id, new_status_id)
        now = datetime.utcnow()
        note_to_add = None

        if new_status_id == RepairStateID.APROBADO:
            repair.approval_date = now
        elif new_status_id == RepairStateID.EN_TRABAJO:
            if not repair.start_date:
                repair.start_date = now
        elif new_status_id == RepairStateID.LISTO:
            repair.completion_date = now
        elif new_status_id == RepairStateID.ENTREGADO:
            repair.delivery_date = now
            new_status_id = RepairStateID.NOVENTENA
            repair.warranty_until = (now + timedelta(days=repair.warranty_days or 90)).date()
        elif new_status_id == RepairStateID.NOVENTENA:
            repair.warranty_until = (now + timedelta(days=repair.warranty_days or 90)).date()
        elif new_status_id == RepairStateID.RECHAZADO:
            repair.archived_at = now
            repair.archived_by = user_id
            note_to_add = "RECHAZADO"
        elif new_status_id == RepairStateID.ARCHIVADO:
            repair.archived_at = now
            repair.archived_by = user_id

        previous_status_id = repair.status_id
        repair.status_id = new_status_id
        repair.updated_at = now

        try:
            if note_to_add:
                self.db.add(
                    RepairNote(
                        repair_id=repair.id,
                        user_id=user_id or 1,
                        note=note_to_add if not notes else f"{note_to_add}: {notes}",
                        note_type="internal",
                    )
                )
            self.db.commit()
            self.db.refresh(repair)

            try:
                create_audit(
                    event_type="repair.status.change",
                    user_id=user_id,
                    details={
                        "repair_id": repair.id,
                        "repair_number": repair.repair_number,
                        "from_status_id": previous_status_id,
                        "to_status_id": new_status_id,
                        "from_status": get_state_name(previous_status_id),
                        "to_status": get_state_name(new_status_id),
                        "notes": notes,
                    },
                    message=f"Estado cambiado: {get_state_name(previous_status_id)} → {get_state_name(new_status_id)}",
                )
            except Exception:
                pass

            self._emit_status_change_event(repair, new_status_id, notes)
            return repair
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error de integridad: {str(exc)}",
            )

    def _emit_status_change_event(
        self,
        repair: Repair,
        new_status_id: int,
        notes: Optional[str] = None,
    ) -> None:
        try:
            client_email = None
            client_name = None
            instrument_name = None

            if hasattr(repair, "device") and repair.device:
                device = repair.device
                if hasattr(device, "client") and device.client:
                    client = device.client
                    client_email = client.email
                    client_name = client.name
                if hasattr(device, "model"):
                    instrument_name = device.model

            if client_email:
                event_bus.emit(
                    Events.REPAIR_STATUS_CHANGED,
                    {
                        "customer_email": client_email,
                        "customer_name": client_name or "Cliente",
                        "repair_id": repair.repair_number,
                        "status": get_state_name(new_status_id),
                        "progress": get_state_progress(new_status_id),
                        "notes": notes,
                    },
                )

                if new_status_id == RepairStateID.LISTO:
                    event_bus.emit(
                        Events.REPAIR_COMPLETED,
                        {
                            "customer_email": client_email,
                            "customer_name": client_name or "Cliente",
                            "repair_id": repair.repair_number,
                            "instrument": instrument_name or "Dispositivo",
                            "total_cost": repair.total_cost or 0,
                        },
                    )
        except Exception as exc:
            logging.getLogger(__name__).error(f"Error emitiendo evento: {str(exc)}")
