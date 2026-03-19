"""
Servicio de escritura para Repair/OT (aditivo).
Encapsula la creación de OT con su lógica de resolución de cliente/dispositivo/código.
"""

from __future__ import annotations

import json
import uuid
from datetime import date as dt_date, datetime
from typing import Dict

from fastapi import BackgroundTasks
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.audit import AuditLog
from app.models.client import Client
from app.models.device import Device
from app.models.device_lookup import DeviceType
from app.models.repair import Repair, RepairStatus
from app.models.repair_intake_sheet import RepairIntakeSheet
from app.models.repair_note import RepairNote
from app.models.repair_photo import RepairPhoto
from app.models.user import User
from app.repositories.repair_repository import RepairRepository
from app.services.email_service import EmailService, build_email_html
from app.services.logging_service import create_audit
from app.services.ot_code_service import (
    client_code as _client_code,
    assign_repair_ot_code,
    ensure_repair_ot_fields,
    next_group_suffix,
    parent_belongs_to_client,
)
from app.services.repair_helpers import resolved_repair_code as _resolved_repair_code
from app.services.whatsapp_service import WhatsAppService
from app.services.repair_service import RepairService


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

    def _parse_optional_date(self, value):
        if not value:
            return None
        if isinstance(value, dt_date):
            return value
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            text = value.strip()
            if not text:
                return None
            try:
                return datetime.fromisoformat(text).date()
            except Exception:
                try:
                    return datetime.strptime(text, "%Y-%m-%d").date()
                except Exception:
                    return None
        return None

    def _to_float(self, value):
        if value in (None, "", "SIN_DATO"):
            return None
        try:
            return float(value)
        except Exception:
            return None

    def _resolve_client(self, client_id: int | None):
        if not client_id:
            return None

        # La UI admin actual envía Client.id. En DBs legacy puede coexistir con
        # User.id numéricamente idéntico, así que debemos privilegiar Client.id.
        client = self.db.query(Client).filter(Client.id == client_id).first()
        if client:
            return client

        user_obj = self.db.query(User).filter(User.id == client_id).first()
        if user_obj:
            linked_client = self.db.query(Client).filter(Client.user_id == user_obj.id).first()
            if linked_client:
                return linked_client

            client = Client(user_id=user_obj.id, name=user_obj.full_name, email=user_obj.email)
            self.db.add(client)
            self.db.flush()
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

    def create_repair_with_audit(
        self,
        repair: Dict,
        user: dict | None,
    ) -> Repair:
        db_repair = self.create_repair(repair)

        try:
            audit_row = AuditLog(
                event_type="repair.create",
                user_id=int(user.get("user_id")) if user and user.get("user_id") else None,
                details={"repair_id": db_repair.id},
                message="Repair created",
            )
            self.db.add(audit_row)
            self.db.commit()
        except Exception:
            try:
                self.db.rollback()
            except Exception:
                pass

        return db_repair

    def update_repair(
        self,
        repair_id: int,
        payload: Dict,
        user_id: int | None = None,
    ) -> tuple[Repair, list[str]]:
        """
        Actualiza una OT/reparación manteniendo comportamiento existente del router.
        Retorna (repair_actualizada, campos_actualizados_sin_status).
        """
        db_repair = self.repo.get_by_id(repair_id)
        if not db_repair:
            raise HTTPException(status_code=404, detail="Repair not found")

        patch = dict(payload or {})
        svc = RepairService(self.db)

        new_status_id = patch.get("status_id")
        if new_status_id is not None and new_status_id != db_repair.status_id:
            db_repair = svc.update_status(
                repair_id=repair_id,
                new_status_id=new_status_id,
                user_id=user_id,
                notes=patch.get("status_notes"),
            )
            patch = {k: v for k, v in patch.items() if k not in ("status_id", "status_notes")}

        updated_fields: list[str] = []
        if patch:
            for key, value in patch.items():
                setattr(db_repair, key, value)
            self.db.commit()
            self.db.refresh(db_repair)
            updated_fields = list(patch.keys())

        return db_repair, updated_fields

    def update_repair_with_audit(
        self,
        repair_id: int,
        payload: Dict,
        user_id: int | None = None,
    ) -> Repair:
        db_repair, updated_fields = self.update_repair(
            repair_id=repair_id,
            payload=payload,
            user_id=user_id,
        )

        if updated_fields:
            try:
                create_audit(
                    event_type="repair.update",
                    user_id=user_id,
                    details={"repair_id": db_repair.id, "fields": updated_fields},
                    message="Repair updated",
                )
            except Exception:
                pass

        return db_repair

    def upsert_repair_intake_sheet(
        self,
        repair_id: int,
        payload: Dict,
        user: dict | None,
    ) -> dict:
        repair = self.repo.get_by_id(repair_id)
        if not repair:
            raise HTTPException(status_code=404, detail="Repair not found")

        device = self.db.query(Device).filter(Device.id == repair.device_id).first()
        if not device:
            raise HTTPException(status_code=400, detail="Repair has no valid device")

        client = self.db.query(Client).filter(Client.id == device.client_id).first()
        if not client:
            raise HTTPException(status_code=400, detail="Repair has no valid client")

        sheet = (
            self.db.query(RepairIntakeSheet)
            .filter(RepairIntakeSheet.repair_id == repair_id)
            .first()
        )
        is_new = sheet is None
        if is_new:
            sheet = RepairIntakeSheet(
                repair_id=repair_id,
                client_id=client.id,
                device_id=device.id,
                created_by=int(user.get("user_id")) if user and user.get("user_id") else None,
            )
            self.db.add(sheet)

        default_client_code = _client_code(client.id)
        default_ot_code = _resolved_repair_code(repair, client.id)
        default_instrument_code = payload.get("instrument_code") or default_ot_code

        sheet.client_id = client.id
        sheet.device_id = device.id
        sheet.client_code = payload.get("client_code") or default_client_code
        sheet.ot_code = payload.get("ot_code") or default_ot_code
        sheet.instrument_code = default_instrument_code
        sheet.equipment_name = payload.get("equipment_name") or device.model
        sheet.equipment_model = payload.get("equipment_model") or device.model
        sheet.equipment_type = payload.get("equipment_type") or "general"
        sheet.requested_service_type = payload.get("requested_service_type") or "maintenance"
        sheet.downtime_description = payload.get("downtime_description")
        sheet.failure_cause = payload.get("failure_cause")
        sheet.repair_tariff = self._to_float(payload.get("repair_tariff"))
        sheet.material_tariff = self._to_float(payload.get("material_tariff"))
        sheet.estimated_repair_time = payload.get("estimated_repair_time")
        sheet.estimated_completion_date = self._parse_optional_date(
            payload.get("estimated_completion_date")
        )
        sheet.operation_department_signed_by = payload.get("operation_department_signed_by")
        sheet.operation_department_signed_at = self._parse_optional_date(
            payload.get("operation_department_signed_at")
        )
        sheet.finance_department_signed_by = payload.get("finance_department_signed_by")
        sheet.finance_department_signed_at = self._parse_optional_date(
            payload.get("finance_department_signed_at")
        )
        sheet.factory_director_signed_by = payload.get("factory_director_signed_by")
        sheet.factory_director_signed_at = self._parse_optional_date(
            payload.get("factory_director_signed_at")
        )
        sheet.general_manager_signed_by = payload.get("general_manager_signed_by")
        sheet.general_manager_signed_at = self._parse_optional_date(
            payload.get("general_manager_signed_at")
        )
        sheet.tabulator_name = payload.get("tabulator_name")
        sheet.form_date = self._parse_optional_date(payload.get("form_date")) or datetime.utcnow().date()
        sheet.annotations = payload.get("annotations")
        sheet.form_payload_json = json.dumps(payload, ensure_ascii=False)

        self.db.commit()
        self.db.refresh(sheet)

        return {"ok": True, "created": is_new, "sheet": sheet}

    def archive_repair(
        self,
        repair_id: int,
        user: dict | None,
    ) -> dict:
        repair = self.repo.get_by_id(repair_id)
        if not repair:
            raise HTTPException(status_code=404, detail="Repair not found")
        repair.archived_at = datetime.utcnow()
        repair.archived_by = int(user.get("user_id")) if user and user.get("user_id") else None
        self.db.commit()
        return {"ok": True, "archived_at": repair.archived_at}

    def notify_client(
        self,
        repair_id: int,
        *,
        background_tasks: BackgroundTasks,
    ) -> dict:
        repair = self.repo.get_by_id(repair_id)
        if not repair:
            raise HTTPException(status_code=404, detail="Repair not found")

        device = self.db.query(Device).filter(Device.id == repair.device_id).first()
        client = (
            self.db.query(Client).filter(Client.id == device.client_id).first()
            if device
            else None
        )
        if not client or not client.email:
            raise HTTPException(status_code=400, detail="Cliente sin email")

        photos = self.db.query(RepairPhoto).filter(RepairPhoto.repair_id == repair.id).all()
        photo_items = []
        if settings.enable_public_uploads:
            for photo in photos[:5]:
                url = photo.photo_url or ""
                if url and url.startswith("/"):
                    url = f"{settings.public_base_url}{url}"
                photo_items.append(
                    f'<img src="{url}" alt="Foto" class="repair-photo-thumb" />'
                )

        summary_html = f"""
        <h2>Resumen de tu OT {repair.repair_number}</h2>
        <p><strong>Cliente:</strong> {client.name}</p>
        <p><strong>Instrumento:</strong> {device.model if device else 'SIN_DATO'}</p>
        <p><strong>Problema:</strong> {repair.problem_reported or 'SIN_DATO'}</p>
        <p><strong>Diagnóstico:</strong> {repair.diagnosis or 'SIN_DATO'}</p>
        <p><strong>Trabajo:</strong> {repair.work_performed or 'SIN_DATO'}</p>
        <p><strong>Total:</strong> ${repair.total_cost or 0:,.0f} CLP</p>
        <div class="repair-photo-gallery">{''.join(photo_items) if photo_items else ''}</div>
        <p>Revisa el detalle completo en tu panel.</p>
        """

        EmailService().send_email(
            to_email=client.email,
            subject=f"Resumen de OT {repair.repair_number}",
            html_content=build_email_html(summary_html),
        )

        if client.phone:
            background_tasks.add_task(
                WhatsAppService().send_text,
                to_phone=client.phone,
                message=(
                    f"Resumen OT {repair.repair_number}: "
                    f"{repair.problem_reported or 'SIN_DATO'}. Revisa el detalle en tu panel."
                ),
            )

        return {"ok": True}

    def reactivate_repair(self, repair_id: int) -> dict:
        repair = self.repo.get_by_id(repair_id)
        if not repair:
            raise HTTPException(status_code=404, detail="Repair not found")
        repair.archived_at = None
        repair.archived_by = None
        repair.status_id = 1
        self.db.commit()
        return {"ok": True, "status_id": repair.status_id}

    def delete_repair_with_audit(
        self,
        repair_id: int,
        user: dict | None,
    ) -> dict:
        existing = self.db.query(Repair.id).filter(Repair.id == repair_id).first()
        if not existing:
            raise HTTPException(status_code=404, detail="Repair not found")

        self.db.query(Repair).filter(Repair.ot_parent_id == repair_id).update(
            {Repair.ot_parent_id: None},
            synchronize_session=False,
        )
        self.db.query(Repair).filter(Repair.id == repair_id).delete(
            synchronize_session=False
        )
        self.db.commit()

        try:
            create_audit(
                event_type="repair.delete",
                user_id=int(user.get("user_id")) if user and user.get("user_id") else None,
                details={"repair_id": repair_id},
                message="Repair deleted",
            )
        except Exception:
            pass

        return {"ok": True}

    def add_repair_note(
        self,
        repair_id: int,
        payload: Dict,
        user: dict | None,
    ) -> RepairNote:
        note_text = payload.get("note")
        if not note_text:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing field: note")

        note = RepairNote(
            repair_id=repair_id,
            user_id=int(user.get("user_id")) if user and user.get("user_id") else None,
            note=note_text,
            note_type=payload.get("note_type", "internal"),
        )
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        return note

    def add_repair_photo(
        self,
        repair_id: int,
        payload: Dict,
    ) -> RepairPhoto:
        photo_url = payload.get("photo_url")
        if not photo_url:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing field: photo_url")

        photo = RepairPhoto(
            repair_id=repair_id,
            photo_url=photo_url,
            photo_type=payload.get("photo_type", "general"),
            caption=payload.get("caption"),
        )
        self.db.add(photo)
        self.db.commit()
        self.db.refresh(photo)
        return photo
