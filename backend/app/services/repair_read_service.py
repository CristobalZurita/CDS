"""
Servicio de lectura para Repair/OT (aditivo).
Encapsula consultas y serialización de lectura del dominio OT.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from fastapi import HTTPException
from sqlalchemy import Integer, String, cast, or_
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.audit import AuditLog
from app.models.client import Client
from app.models.device import Device
from app.models.repair import Repair, RepairStatus
from app.models.repair_component_usage import RepairComponentUsage
from app.models.repair_intake_sheet import RepairIntakeSheet
from app.models.repair_note import RepairNote
from app.models.repair_photo import RepairPhoto
from app.repositories.repair_repository import RepairRepository
from app.services.ot_code_service import (
    client_code as _client_code,
    next_group_suffix,
    parent_belongs_to_client,
    repair_code as _repair_code,
)
from app.services.repair_helpers import (
    auto_archive_repairs as _auto_archive_repairs,
    resolved_repair_code as _resolved_repair_code,
)
from app.services.repair_state_machine import (
    get_allowed_transitions,
    get_state_code,
)


class RepairReadService:
    """Capa de lectura (query) para OT."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = RepairRepository(db)

    def list_active(self):
        return self.repo.list_active()

    def list_archived(self):
        return self.repo.list_archived()

    def get_by_id(self, repair_id: int) -> Optional[Repair]:
        return self.repo.get_by_id(repair_id)

    def get_last_created(self) -> Optional[Repair]:
        return self.repo.get_last_created()

    def serialize_intake_sheet(self, sheet: RepairIntakeSheet) -> dict[str, Any]:
        return {
            "id": sheet.id,
            "repair_id": sheet.repair_id,
            "client_id": sheet.client_id,
            "device_id": sheet.device_id,
            "client_code": sheet.client_code,
            "ot_code": sheet.ot_code,
            "instrument_code": sheet.instrument_code,
            "equipment_name": sheet.equipment_name,
            "equipment_model": sheet.equipment_model,
            "equipment_type": sheet.equipment_type,
            "requested_service_type": sheet.requested_service_type,
            "downtime_description": sheet.downtime_description,
            "failure_cause": sheet.failure_cause,
            "repair_tariff": sheet.repair_tariff,
            "material_tariff": sheet.material_tariff,
            "estimated_repair_time": sheet.estimated_repair_time,
            "estimated_completion_date": sheet.estimated_completion_date.isoformat()
            if sheet.estimated_completion_date
            else None,
            "operation_department_signed_by": sheet.operation_department_signed_by,
            "operation_department_signed_at": sheet.operation_department_signed_at.isoformat()
            if sheet.operation_department_signed_at
            else None,
            "finance_department_signed_by": sheet.finance_department_signed_by,
            "finance_department_signed_at": sheet.finance_department_signed_at.isoformat()
            if sheet.finance_department_signed_at
            else None,
            "factory_director_signed_by": sheet.factory_director_signed_by,
            "factory_director_signed_at": sheet.factory_director_signed_at.isoformat()
            if sheet.factory_director_signed_at
            else None,
            "general_manager_signed_by": sheet.general_manager_signed_by,
            "general_manager_signed_at": sheet.general_manager_signed_at.isoformat()
            if sheet.general_manager_signed_at
            else None,
            "tabulator_name": sheet.tabulator_name,
            "form_date": sheet.form_date.isoformat() if sheet.form_date else None,
            "annotations": sheet.annotations,
            "created_at": sheet.created_at.isoformat() if sheet.created_at else None,
            "updated_at": sheet.updated_at.isoformat() if sheet.updated_at else None,
        }

    def _get_repair_device_client(
        self,
        repair: Repair,
    ) -> tuple[Device | None, Client | None]:
        device = self.db.query(Device).filter(Device.id == repair.device_id).first()
        client = (
            self.db.query(Client).filter(Client.id == device.client_id).first()
            if device
            else None
        )
        return device, client

    def _repair_payload(self, repair: Repair) -> dict[str, Any]:
        device, client = self._get_repair_device_client(repair)
        repair_code = _resolved_repair_code(repair, client.id if client else None)
        return {
            "id": repair.id,
            "repair_number": repair.repair_number,
            "repair_code": repair_code,
            "client_id": client.id if client else None,
            "client_code": _client_code(client.id) if client else None,
            "client_name": client.name if client else None,
            "device_id": device.id if device else None,
            "device_model": device.model if device else None,
            "status": repair.status,
            "status_id": repair.status_id,
            "ot_parent_id": repair.ot_parent_id,
            "ot_sequence": repair.ot_sequence,
            "problem_reported": repair.problem_reported,
            "created_at": repair.created_at.isoformat() if repair.created_at else None,
            "archived_at": repair.archived_at.isoformat() if repair.archived_at else None,
        }

    def list_active_payloads(
        self,
        *,
        limit: int | None = None,
        sort: str | None = None,
    ) -> list[dict[str, Any]]:
        _auto_archive_repairs(self.db)
        result = [self._repair_payload(repair) for repair in self.list_active()]
        if sort == "-created_at":
            result.sort(key=lambda repair: repair.get("created_at") or "", reverse=True)
        elif sort == "created_at":
            result.sort(key=lambda repair: repair.get("created_at") or "")
        if limit is not None and limit > 0:
            result = result[:limit]
        return result

    def list_archived_payloads(self) -> list[dict[str, Any]]:
        _auto_archive_repairs(self.db)
        return [self._repair_payload(repair) for repair in self.list_archived()]

    def get_next_repair_code_payload(
        self,
        *,
        client_id: int,
        ot_parent_id: int | None = None,
    ) -> dict[str, Any]:
        client = self.db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

        if ot_parent_id is not None:
            parent = self.get_by_id(int(ot_parent_id))
            if not parent:
                raise HTTPException(status_code=404, detail="Parent repair not found")

            if not parent_belongs_to_client(self.db, parent, client.id):
                raise HTTPException(
                    status_code=400,
                    detail="Parent repair does not belong to provided client",
                )

            base_code = _repair_code(client.id, parent.id)
            next_suffix = next_group_suffix(self.db, client.id, parent)

            return {
                "client_id": client.id,
                "client_code": _client_code(client.id),
                "ot_parent_id": parent.id,
                "ot_base_code": base_code,
                "next_suffix": next_suffix,
                "repair_code": _repair_code(client.id, parent.id, next_suffix),
            }

        last_repair = self.get_last_created()
        next_repair_id = (last_repair.id + 1) if last_repair else 1
        return {
            "client_id": client.id,
            "client_code": _client_code(client.id),
            "next_repair_id": next_repair_id,
            "ot_base_code": _repair_code(client.id, next_repair_id),
            "repair_code": _repair_code(client.id, next_repair_id),
        }

    def get_repair_detail_payload(self, repair_id: int) -> dict[str, Any]:
        repair = self.get_by_id(repair_id)
        if not repair:
            raise HTTPException(status_code=404, detail="Repair not found")

        device, client = self._get_repair_device_client(repair)
        repair_code = _resolved_repair_code(repair, client.id if client else None)
        current_status_code = (
            repair.status_obj.code
            if repair.status_obj and repair.status_obj.code
            else get_state_code(repair.status_id)
        )
        allowed_status_ids = [repair.status_id, *sorted(get_allowed_transitions(repair.status_id))]
        intake_sheet = (
            self.db.query(RepairIntakeSheet)
            .filter(RepairIntakeSheet.repair_id == repair.id)
            .first()
        )
        return {
            "id": repair.id,
            "repair_number": repair.repair_number,
            "repair_code": repair_code,
            "client": {
                "id": client.id,
                "name": client.name,
                "client_code": _client_code(client.id),
            }
            if client
            else None,
            "device": {
                "id": device.id,
                "model": device.model,
                "serial_number": device.serial_number,
            }
            if device
            else None,
            "status_id": repair.status_id,
            "status": repair.status,
            "status_code": current_status_code,
            "allowed_status_ids": allowed_status_ids,
            "ot_parent_id": repair.ot_parent_id,
            "ot_sequence": repair.ot_sequence,
            "priority": repair.priority,
            "problem_reported": repair.problem_reported,
            "diagnosis": repair.diagnosis,
            "work_performed": repair.work_performed,
            "parts_cost": repair.parts_cost,
            "labor_cost": repair.labor_cost,
            "additional_cost": repair.additional_cost,
            "discount": repair.discount,
            "total_cost": repair.total_cost,
            "paid_amount": repair.paid_amount,
            "payment_status": repair.payment_status,
            "payment_method": repair.payment_method,
            "signature_ingreso_path": repair.signature_ingreso_path,
            "signature_retiro_path": repair.signature_retiro_path,
            "archived_at": repair.archived_at.isoformat() if repair.archived_at else None,
            "intake_sheet": self.serialize_intake_sheet(intake_sheet)
            if intake_sheet
            else None,
        }

    def get_closure_payload(self, repair_id: int) -> dict[str, Any]:
        repair = self.get_by_id(repair_id)
        if not repair:
            raise HTTPException(status_code=404, detail="Repair not found")

        device, client = self._get_repair_device_client(repair)
        status_obj = (
            self.db.query(RepairStatus).filter(RepairStatus.id == repair.status_id).first()
        )
        intake_sheet = (
            self.db.query(RepairIntakeSheet)
            .filter(RepairIntakeSheet.repair_id == repair.id)
            .first()
        )
        notes = (
            self.db.query(RepairNote)
            .filter(RepairNote.repair_id == repair.id)
            .order_by(RepairNote.created_at.asc())
            .all()
        )
        components = (
            self.db.query(RepairComponentUsage)
            .filter(RepairComponentUsage.repair_id == repair.id)
            .order_by(RepairComponentUsage.created_at.asc())
            .all()
        )
        photos_count = (
            self.db.query(RepairPhoto).filter(RepairPhoto.repair_id == repair.id).count()
        )
        repair_code = _resolved_repair_code(repair, client.id if client else None)

        return {
            "repair_id": repair.id,
            "repair_number": repair.repair_number,
            "repair_code": repair_code,
            "status_id": repair.status_id,
            "status_name": status_obj.name if status_obj else repair.status,
            "intake_date": repair.intake_date,
            "diagnosis_date": repair.diagnosis_date,
            "start_date": repair.start_date,
            "completion_date": repair.completion_date,
            "delivery_date": repair.delivery_date,
            "problem_reported": repair.problem_reported,
            "diagnosis": repair.diagnosis,
            "work_performed": repair.work_performed,
            "parts_cost": repair.parts_cost,
            "labor_cost": repair.labor_cost,
            "additional_cost": repair.additional_cost,
            "discount": repair.discount,
            "total_cost": repair.total_cost,
            "paid_amount": repair.paid_amount,
            "payment_status": repair.payment_status,
            "payment_method": repair.payment_method,
            "signature_ingreso_path": repair.signature_ingreso_path,
            "signature_retiro_path": repair.signature_retiro_path,
            "client_name": client.name if client else None,
            "client_email": client.email if client else None,
            "client_phone": client.phone if client else None,
            "device_model": device.model if device else None,
            "device_serial": device.serial_number if device else None,
            "components": [
                {
                    "component_table": component.component_table,
                    "component_id": component.component_id,
                    "quantity": component.quantity,
                    "unit_cost": component.unit_cost or 0,
                    "total_cost": component.total_cost,
                    "notes": component.notes,
                }
                for component in components
            ],
            "notes": [
                {
                    "id": note.id,
                    "note_type": note.note_type,
                    "note": note.note,
                    "created_at": note.created_at,
                }
                for note in notes
            ],
            "photos_count": photos_count,
            "intake_sheet": self.serialize_intake_sheet(intake_sheet)
            if intake_sheet
            else None,
        }

    def get_repair_intake_sheet_payload(self, repair_id: int) -> dict[str, Any]:
        sheet = (
            self.db.query(RepairIntakeSheet)
            .filter(RepairIntakeSheet.repair_id == repair_id)
            .first()
        )
        if not sheet:
            raise HTTPException(status_code=404, detail="Repair intake sheet not found")
        return {"sheet": self.serialize_intake_sheet(sheet)}

    def list_repair_audit(self, repair_id: int):
        query = (
            self.db.query(AuditLog)
            .filter(AuditLog.event_type.like("repair.%"))
            .order_by(AuditLog.created_at.desc())
        )

        try:
            return (
                query
                .filter(
                    or_(
                        AuditLog.details["repair_id"].as_integer() == repair_id,
                        cast(AuditLog.details["repair_id"].as_string(), Integer) == repair_id,
                        cast(AuditLog.details["repair_id"].as_string(), String) == str(repair_id),
                    )
                )
                .limit(200)
                .all()
            )
        except Exception:
            logs = query.limit(200).all()
            filtered = []
            for log in logs:
                details = log.details or {}
                if details.get("repair_id") == repair_id:
                    filtered.append(log)
            return filtered

    def list_repair_notes(self, repair_id: int):
        return (
            self.db.query(RepairNote)
            .filter(RepairNote.repair_id == repair_id)
            .order_by(RepairNote.created_at.desc())
            .all()
        )

    def list_repair_photos(self, repair_id: int):
        photos = (
            self.db.query(RepairPhoto)
            .filter(RepairPhoto.repair_id == repair_id)
            .order_by(RepairPhoto.sort_order.asc(), RepairPhoto.created_at.desc())
            .all()
        )
        if settings.enable_public_uploads:
            return photos
        return [
            {
                "id": photo.id,
                "photo_url": None,
                "photo_download_url": f"/api/v1/files/repair-photos/{photo.id}",
                "photo_type": photo.photo_type,
                "caption": photo.caption,
                "created_at": photo.created_at,
                "sort_order": photo.sort_order,
            }
            for photo in photos
        ]
