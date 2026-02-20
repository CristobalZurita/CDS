"""
Servicio de escritura para Repair/OT (aditivo).
Encapsula la creación de OT con su lógica de resolución de cliente/dispositivo/código.
"""

from __future__ import annotations

import uuid
from typing import Dict

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.device import Device
from app.models.device_lookup import DeviceType
from app.models.repair import Repair, RepairStatus
from app.models.user import User
from app.repositories.repair_repository import RepairRepository
from app.services.ot_code_service import (
    assign_repair_ot_code,
    ensure_repair_ot_fields,
    next_group_suffix,
    parent_belongs_to_client,
)


class RepairWriteService:
    """Capa de escritura (command) para OT."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = RepairRepository(db)

    def _ensure_default_device_type(self):
        dt = self.db.query(DeviceType).first()
        if not dt:
            dt = DeviceType(code="generic", name="Generic", description="Autocreated")
            self.db.add(dt)
            self.db.flush()
        return dt

    def _ensure_default_status(self):
        st = self.db.query(RepairStatus).filter(RepairStatus.id == 1).first()
        if not st:
            st = RepairStatus(id=1, code="ingreso", name="Ingreso", description="Autocreated")
            self.db.add(st)
            self.db.flush()
        return st

    def _resolve_client(self, client_id: int | None):
        if not client_id:
            return None

        user_obj = self.db.query(User).filter(User.id == client_id).first()
        if user_obj:
            linked_client = self.db.query(Client).filter(Client.user_id == user_obj.id).first()
            if linked_client:
                return linked_client

            legacy_client = self.db.query(Client).filter(Client.id == client_id).first()
            if legacy_client and (legacy_client.user_id is None or legacy_client.user_id == user_obj.id):
                if legacy_client.user_id is None:
                    legacy_client.user_id = user_obj.id
                    self.db.flush()
                return legacy_client

            client = Client(user_id=user_obj.id, name=user_obj.full_name, email=user_obj.email)
            self.db.add(client)
            self.db.flush()
            return client

        client = self.db.query(Client).filter(Client.id == client_id).first()
        if client:
            return client
        return None

    def create_repair(self, repair: Dict) -> Repair:
        self._ensure_default_status()

        device_id = repair.get("device_id")
        if not device_id:
            client = self._resolve_client(repair.get("client_id"))
            if client:
                dt = self._ensure_default_device_type()
                device = Device(
                    client_id=client.id,
                    device_type_id=dt.id,
                    model=repair.get("model") or repair.get("title") or "Unknown",
                )
                self.db.add(device)
                self.db.flush()
                device_id = device.id

        if not device_id:
            raise HTTPException(status_code=400, detail="device_id or client_id required")

        explicit_repair_number = repair.get("repair_number")
        parent_id = repair.get("ot_parent_id") or repair.get("ot_base_repair_id")
        requested_suffix = repair.get("ot_suffix")

        db_repair = Repair(
            repair_number=explicit_repair_number or f"R-{uuid.uuid4().hex[:8]}",
            device_id=device_id,
            quote_id=repair.get("quote_id"),
            status_id=repair.get("status_id") or 1,
            assigned_to=repair.get("assigned_to"),
            problem_reported=repair.get("problem_reported")
            or repair.get("description")
            or repair.get("title")
            or "Sin detalle",
            diagnosis=repair.get("diagnosis"),
            work_performed=repair.get("work_performed"),
            parts_cost=repair.get("parts_cost", 0),
            labor_cost=repair.get("labor_cost", 0),
            additional_cost=repair.get("additional_cost", 0),
            discount=repair.get("discount", 0),
            total_cost=repair.get("total_cost", 0),
            payment_status=repair.get("payment_status") or "pending",
            payment_method=repair.get("payment_method"),
            paid_amount=repair.get("paid_amount", 0),
            priority=repair.get("priority", 2),
        )
        self.db.add(db_repair)
        self.db.flush()

        device = self.db.query(Device).filter(Device.id == db_repair.device_id).first()
        client_id = device.client_id if device else None

        parent_repair = None
        if parent_id is not None:
            try:
                parent_lookup_id = int(parent_id)
            except (TypeError, ValueError):
                raise HTTPException(status_code=400, detail="Invalid ot_parent_id")

            parent_repair = self.repo.get_by_id(parent_lookup_id)
            if not parent_repair:
                raise HTTPException(status_code=404, detail="Parent repair not found")
            if client_id and not parent_belongs_to_client(self.db, parent_repair, int(client_id)):
                raise HTTPException(status_code=400, detail="Parent repair does not belong to device client")

        if client_id:
            if explicit_repair_number:
                if parent_repair:
                    candidate_sequence = None
                    if requested_suffix is not None:
                        try:
                            candidate = int(requested_suffix)
                        except (TypeError, ValueError):
                            candidate = 0
                        if candidate > 0:
                            collision = (
                                self.db.query(Repair.id)
                                .filter(
                                    Repair.ot_parent_id == parent_repair.id,
                                    Repair.ot_sequence == candidate,
                                )
                                .first()
                            )
                            if not collision:
                                candidate_sequence = candidate

                    if candidate_sequence is None:
                        candidate_sequence = next_group_suffix(self.db, int(client_id), parent_repair)

                    db_repair.ot_parent_id = parent_repair.id
                    db_repair.ot_sequence = candidate_sequence
                else:
                    ensure_repair_ot_fields(self.db, db_repair)
            else:
                assign_repair_ot_code(
                    db=self.db,
                    repair=db_repair,
                    client_id=int(client_id),
                    parent_repair=parent_repair,
                    requested_suffix=requested_suffix,
                )

        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=409,
                detail="Conflict creating repair. Verify OT code and sequence uniqueness.",
            ) from exc

        return db_repair
