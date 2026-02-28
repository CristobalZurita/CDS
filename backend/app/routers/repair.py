"""
Router de Reparaciones
======================
Endpoints para gestión de reparaciones.
Usa permisos granulares (require_permission).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.models.repair import Repair, RepairStatus
from app.models.audit import AuditLog
from typing import Dict
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_permission
from app.services.logging_service import create_audit
from app.services.repair_service import RepairService
from app.models.repair_note import RepairNote
from app.models.repair_photo import RepairPhoto
from app.models.device import Device
from app.models.client import Client
from app.models.repair_intake_sheet import RepairIntakeSheet
from datetime import date as dt_date, datetime, timedelta
import json
from app.core.config import settings
from app.services.email_service import EmailService, build_email_html
from app.services.whatsapp_service import WhatsAppService
from app.services.pdf_generator import generate_repair_closure_pdf_bytes
from app.services.repair_read_service import RepairReadService
from app.services.repair_write_service import RepairWriteService
from app.services.ot_code_service import (
    client_code as _client_code,
    next_group_suffix,
    parent_belongs_to_client,
    repair_code as _repair_code,
)
from app.models.repair_component_usage import RepairComponentUsage

router = APIRouter(prefix="/repairs", tags=["repairs"])


def _auto_archive_repairs(db: Session) -> None:
    cutoff = datetime.utcnow() - timedelta(days=90)
    to_archive = (
        db.query(Repair)
        .filter(Repair.delivery_date.isnot(None))
        .filter(Repair.archived_at.is_(None))
        .filter(Repair.delivery_date <= cutoff)
        .all()
    )
    if not to_archive:
        return
    for r in to_archive:
        r.archived_at = datetime.utcnow()
        r.status_id = 9
    db.commit()


def _repair_payload(repair: Repair, db: Session) -> Dict:
    device = db.query(Device).filter(Device.id == repair.device_id).first()
    client = db.query(Client).filter(Client.id == device.client_id).first() if device else None
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
        "archived_at": repair.archived_at.isoformat() if repair.archived_at else None
    }


def _resolved_repair_code(repair: Repair, client_id: int | None) -> str:
    if repair.repair_number and not str(repair.repair_number).startswith("R-"):
        return repair.repair_number
    if not client_id:
        return repair.repair_number

    if repair.ot_parent_id and repair.ot_sequence:
        if repair.ot_parent_id == repair.id:
            if int(repair.ot_sequence) <= 1:
                return _repair_code(client_id, repair.id)
            return _repair_code(client_id, repair.id, int(repair.ot_sequence))
        return _repair_code(client_id, int(repair.ot_parent_id), int(repair.ot_sequence))

    return _repair_code(client_id, repair.id)


def _parse_optional_date(value):
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


def _to_float(value):
    if value in (None, "", "SIN_DATO"):
        return None
    try:
        return float(value)
    except Exception:
        return None


def _serialize_intake_sheet(sheet: RepairIntakeSheet) -> Dict:
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
        "estimated_completion_date": sheet.estimated_completion_date.isoformat() if sheet.estimated_completion_date else None,
        "operation_department_signed_by": sheet.operation_department_signed_by,
        "operation_department_signed_at": sheet.operation_department_signed_at.isoformat() if sheet.operation_department_signed_at else None,
        "finance_department_signed_by": sheet.finance_department_signed_by,
        "finance_department_signed_at": sheet.finance_department_signed_at.isoformat() if sheet.finance_department_signed_at else None,
        "factory_director_signed_by": sheet.factory_director_signed_by,
        "factory_director_signed_at": sheet.factory_director_signed_at.isoformat() if sheet.factory_director_signed_at else None,
        "general_manager_signed_by": sheet.general_manager_signed_by,
        "general_manager_signed_at": sheet.general_manager_signed_at.isoformat() if sheet.general_manager_signed_at else None,
        "tabulator_name": sheet.tabulator_name,
        "form_date": sheet.form_date.isoformat() if sheet.form_date else None,
        "annotations": sheet.annotations,
        "created_at": sheet.created_at.isoformat() if sheet.created_at else None,
        "updated_at": sheet.updated_at.isoformat() if sheet.updated_at else None,
    }


def _build_repair_closure_payload(repair: Repair, db: Session) -> Dict:
    device = db.query(Device).filter(Device.id == repair.device_id).first()
    client = db.query(Client).filter(Client.id == device.client_id).first() if device else None
    status_obj = db.query(RepairStatus).filter(RepairStatus.id == repair.status_id).first()
    intake_sheet = (
        db.query(RepairIntakeSheet)
        .filter(RepairIntakeSheet.repair_id == repair.id)
        .first()
    )
    notes = (
        db.query(RepairNote)
        .filter(RepairNote.repair_id == repair.id)
        .order_by(RepairNote.created_at.asc())
        .all()
    )
    components = (
        db.query(RepairComponentUsage)
        .filter(RepairComponentUsage.repair_id == repair.id)
        .order_by(RepairComponentUsage.created_at.asc())
        .all()
    )
    photos_count = db.query(RepairPhoto).filter(RepairPhoto.repair_id == repair.id).count()
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
                "component_table": c.component_table,
                "component_id": c.component_id,
                "quantity": c.quantity,
                "unit_cost": c.unit_cost or 0,
                "total_cost": c.total_cost,
                "notes": c.notes,
            }
            for c in components
        ],
        "notes": [
            {
                "id": n.id,
                "note_type": n.note_type,
                "note": n.note,
                "created_at": n.created_at,
            }
            for n in notes
        ],
        "photos_count": photos_count,
        "intake_sheet": _serialize_intake_sheet(intake_sheet) if intake_sheet else None,
    }


def _safe_pdf_filename(value: str) -> str:
    text = str(value or "OT").strip()
    if not text:
        text = "OT"
    sanitized = []
    for char in text:
        if char.isalnum() or char in ("-", "_", "."):
            sanitized.append(char)
        else:
            sanitized.append("_")
    return "".join(sanitized)


@router.get("")
@router.get("/")
def list_repairs(
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "read"))
):
    _auto_archive_repairs(db)
    repairs = RepairReadService(db).list_active()
    return [_repair_payload(repair, db) for repair in repairs]


@router.get("/archived")
def list_archived_repairs(
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "read"))
):
    _auto_archive_repairs(db)
    repairs = RepairReadService(db).list_archived()
    return [_repair_payload(repair, db) for repair in repairs]


@router.get("/next-code")
def get_next_repair_code(
    client_id: int,
    ot_parent_id: int | None = None,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "read"))
):
    """
    Entrega código OT sugerido usando la nomenclatura oficial backend.

    - Sin `ot_parent_id`: sugiere próximo OT base (`CDS-XXX-OT-NNN`).
    - Con `ot_parent_id`: sugiere próximo código agrupado (`...-NN`).
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    if ot_parent_id is not None:
        read_svc = RepairReadService(db)
        parent = read_svc.get_by_id(int(ot_parent_id))
        if not parent:
            raise HTTPException(status_code=404, detail="Parent repair not found")

        if not parent_belongs_to_client(db, parent, client.id):
            raise HTTPException(status_code=400, detail="Parent repair does not belong to provided client")

        base_code = _repair_code(client.id, parent.id)
        next_suffix = next_group_suffix(db, client.id, parent)

        return {
            "client_id": client.id,
            "client_code": _client_code(client.id),
            "ot_parent_id": parent.id,
            "ot_base_code": base_code,
            "next_suffix": next_suffix,
            "repair_code": _repair_code(client.id, parent.id, next_suffix),
        }

    last_repair = RepairReadService(db).get_last_created()
    next_repair_id = (last_repair.id + 1) if last_repair else 1
    return {
        "client_id": client.id,
        "client_code": _client_code(client.id),
        "next_repair_id": next_repair_id,
        "ot_base_code": _repair_code(client.id, next_repair_id),
        "repair_code": _repair_code(client.id, next_repair_id),
    }


@router.post("", status_code=status.HTTP_201_CREATED)
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_repair(
    repair: Dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "create"))
):
    db_repair = RepairWriteService(db).create_repair(repair)

    # Audit: repair created
    try:
        audit_row = AuditLog(
            event_type="repair.create",
            user_id=int(user.get("user_id")) if user and user.get("user_id") else None,
            details={"repair_id": db_repair.id},
            message="Repair created",
        )
        db.add(audit_row)
        db.commit()
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass
        pass
    return db_repair


@router.get("/{repair_id}")
def get_repair(
    repair_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "read"))
):
    repair = RepairReadService(db).get_by_id(repair_id)
    if not repair:
        raise HTTPException(status_code=404, detail="Repair not found")
    device = db.query(Device).filter(Device.id == repair.device_id).first()
    client = db.query(Client).filter(Client.id == device.client_id).first() if device else None
    repair_code = _resolved_repair_code(repair, client.id if client else None)
    intake_sheet = (
        db.query(RepairIntakeSheet)
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
            "client_code": _client_code(client.id)
        } if client else None,
        "device": {
            "id": device.id,
            "model": device.model,
            "serial_number": device.serial_number
        } if device else None,
        "status_id": repair.status_id,
        "status": repair.status,
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
        "intake_sheet": _serialize_intake_sheet(intake_sheet) if intake_sheet else None,
    }


@router.get("/{repair_id}/closure-pdf")
def download_repair_closure_pdf(
    repair_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "update")),
):
    repair = db.query(Repair).filter(Repair.id == repair_id).first()
    if not repair:
        raise HTTPException(status_code=404, detail="Repair not found")

    payload = _build_repair_closure_payload(repair, db)
    pdf_bytes = generate_repair_closure_pdf_bytes(payload)

    file_code = payload.get("repair_code") or payload.get("repair_number") or f"OT_{repair_id}"
    safe_code = _safe_pdf_filename(str(file_code))
    filename = f"CIERRE_{safe_code}.pdf"

    try:
        create_audit(
            event_type="repair.closure_pdf.download",
            user_id=int(user.get("user_id")) if user and user.get("user_id") else None,
            details={"repair_id": repair_id, "filename": filename},
            message=f"Closure PDF generated for repair #{repair_id}",
        )
    except Exception:
        pass

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{repair_id}/intake-sheet")
def get_repair_intake_sheet(
    repair_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "read"))
):
    sheet = (
        db.query(RepairIntakeSheet)
        .filter(RepairIntakeSheet.repair_id == repair_id)
        .first()
    )
    if not sheet:
        raise HTTPException(status_code=404, detail="Repair intake sheet not found")
    return {"sheet": _serialize_intake_sheet(sheet)}


@router.post("/{repair_id}/intake-sheet", status_code=status.HTTP_201_CREATED)
def upsert_repair_intake_sheet(
    repair_id: int,
    payload: Dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "update"))
):
    repair = db.query(Repair).filter(Repair.id == repair_id).first()
    if not repair:
        raise HTTPException(status_code=404, detail="Repair not found")

    device = db.query(Device).filter(Device.id == repair.device_id).first()
    if not device:
        raise HTTPException(status_code=400, detail="Repair has no valid device")

    client = db.query(Client).filter(Client.id == device.client_id).first()
    if not client:
        raise HTTPException(status_code=400, detail="Repair has no valid client")

    sheet = (
        db.query(RepairIntakeSheet)
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
        db.add(sheet)

    # Base identifiers (nomenclatura)
    default_client_code = _client_code(client.id)
    default_ot_code = _resolved_repair_code(repair, client.id)
    default_instrument_code = payload.get("instrument_code") or default_ot_code

    sheet.client_id = client.id
    sheet.device_id = device.id
    sheet.client_code = payload.get("client_code") or default_client_code
    sheet.ot_code = payload.get("ot_code") or default_ot_code
    sheet.instrument_code = default_instrument_code

    # Equipo/servicio
    sheet.equipment_name = payload.get("equipment_name") or device.model
    sheet.equipment_model = payload.get("equipment_model") or device.model
    sheet.equipment_type = payload.get("equipment_type") or "general"
    sheet.requested_service_type = payload.get("requested_service_type") or "maintenance"
    sheet.downtime_description = payload.get("downtime_description")
    sheet.failure_cause = payload.get("failure_cause")

    # Costos/plan
    sheet.repair_tariff = _to_float(payload.get("repair_tariff"))
    sheet.material_tariff = _to_float(payload.get("material_tariff"))
    sheet.estimated_repair_time = payload.get("estimated_repair_time")
    sheet.estimated_completion_date = _parse_optional_date(payload.get("estimated_completion_date"))

    # Aprobaciones por área
    sheet.operation_department_signed_by = payload.get("operation_department_signed_by")
    sheet.operation_department_signed_at = _parse_optional_date(payload.get("operation_department_signed_at"))
    sheet.finance_department_signed_by = payload.get("finance_department_signed_by")
    sheet.finance_department_signed_at = _parse_optional_date(payload.get("finance_department_signed_at"))
    sheet.factory_director_signed_by = payload.get("factory_director_signed_by")
    sheet.factory_director_signed_at = _parse_optional_date(payload.get("factory_director_signed_at"))
    sheet.general_manager_signed_by = payload.get("general_manager_signed_by")
    sheet.general_manager_signed_at = _parse_optional_date(payload.get("general_manager_signed_at"))

    sheet.tabulator_name = payload.get("tabulator_name")
    sheet.form_date = _parse_optional_date(payload.get("form_date")) or datetime.utcnow().date()
    sheet.annotations = payload.get("annotations")
    sheet.form_payload_json = json.dumps(payload, ensure_ascii=False)

    db.commit()
    db.refresh(sheet)
    return {
        "ok": True,
        "created": is_new,
        "sheet": _serialize_intake_sheet(sheet),
    }


@router.post("/{repair_id}/archive")
def archive_repair(
    repair_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "update"))
):
    repair = db.query(Repair).filter(Repair.id == repair_id).first()
    if not repair:
        raise HTTPException(status_code=404, detail="Repair not found")
    repair.archived_at = datetime.utcnow()
    repair.archived_by = int(user.get("user_id")) if user and user.get("user_id") else None
    db.commit()
    return {"ok": True, "archived_at": repair.archived_at}


@router.post("/{repair_id}/notify")
def notify_client(
    repair_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "update"))
):
    repair = db.query(Repair).filter(Repair.id == repair_id).first()
    if not repair:
        raise HTTPException(status_code=404, detail="Repair not found")
    device = db.query(Device).filter(Device.id == repair.device_id).first()
    client = db.query(Client).filter(Client.id == device.client_id).first() if device else None
    if not client or not client.email:
        raise HTTPException(status_code=400, detail="Cliente sin email")

    photos = db.query(RepairPhoto).filter(RepairPhoto.repair_id == repair.id).all()
    photo_items = []
    if settings.enable_public_uploads:
        for p in photos[:5]:
            url = p.photo_url or ""
            if url and url.startswith("/"):
                url = f"{settings.public_base_url}{url}"
            photo_items.append(f'<img src="{url}" alt="Foto" class="repair-photo-thumb" />')

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

    wrapped_summary_html = build_email_html(summary_html)

    EmailService().send_email(
        to_email=client.email,
        subject=f"Resumen de OT {repair.repair_number}",
        html_content=wrapped_summary_html
    )

    if client.phone:
        WhatsAppService().send_text(
            to_phone=client.phone,
            message=f"Resumen OT {repair.repair_number}: {repair.problem_reported or 'SIN_DATO'}. Revisa el detalle en tu panel."
        )

    return {"ok": True}


@router.post("/{repair_id}/reactivate")
def reactivate_repair(
    repair_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "update"))
):
    repair = db.query(Repair).filter(Repair.id == repair_id).first()
    if not repair:
        raise HTTPException(status_code=404, detail="Repair not found")
    repair.archived_at = None
    repair.archived_by = None
    repair.status_id = 1
    db.commit()
    return {"ok": True, "status_id": repair.status_id}


@router.put("/{repair_id}")
def update_repair(
    repair_id: int,
    repair: Dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "update"))
):
    user_id = int(user.get("user_id")) if user and user.get("user_id") else None
    db_repair, updated_fields = RepairWriteService(db).update_repair(
        repair_id=repair_id,
        payload=repair,
        user_id=user_id,
    )

    # Audit: repair updated (campos no-status)
    if updated_fields:
        try:
            create_audit(
                event_type="repair.update",
                user_id=user_id,
                details={"repair_id": db_repair.id, "fields": updated_fields},
                message="Repair updated"
            )
        except Exception:
            pass

    return db_repair


@router.delete("/{repair_id}")
def delete_repair(
    repair_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "delete"))
):
    existing = db.query(Repair.id).filter(Repair.id == repair_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Repair not found")

    # Break OT parent links in SQL first so self-referential repairs do not
    # trigger circular dependency resolution inside the ORM unit of work.
    db.query(Repair).filter(Repair.ot_parent_id == repair_id).update(
        {Repair.ot_parent_id: None},
        synchronize_session=False,
    )
    db.query(Repair).filter(Repair.id == repair_id).delete(synchronize_session=False)
    db.commit()
    # Audit: repair deleted
    try:
        create_audit(
            event_type="repair.delete",
            user_id=int(user.get("user_id")) if user and user.get("user_id") else None,
            details={"repair_id": repair_id},
            message="Repair deleted"
        )
    except Exception:
        pass
    return {"ok": True}


@router.get("/{repair_id}/audit")
def get_repair_audit(repair_id: int, db: Session = Depends(get_db), user: dict = Depends(require_permission("repairs", "read"))):
    logs = (
        db.query(AuditLog)
        .filter(AuditLog.event_type.like("repair.%"))
        .order_by(AuditLog.created_at.desc())
        .limit(200)
        .all()
    )
    filtered = []
    for log in logs:
        details = log.details or {}
        if details.get("repair_id") == repair_id:
            filtered.append(log)
    return filtered


# ---------------------------------------------------------------------------
# Endpoints that use RepairService for transactional operations
# ---------------------------------------------------------------------------


@router.post("/{repair_id}/components", status_code=status.HTTP_201_CREATED)
def add_component_usage(repair_id: int, payload: Dict, db: Session = Depends(get_db), user: dict = Depends(require_permission("repairs", "update"))):
    """Registrar uso de un componente en una reparación y descontar stock"""
    required = ("component_table", "component_id", "quantity")
    for k in required:
        if k not in payload:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Missing field: {k}")

    svc = RepairService(db)
    try:
        from_reserved = str(payload.get("from_reserved", "false")).strip().lower() in ("1", "true", "yes", "on")
        usage = svc.add_component_usage(
            repair_id=repair_id,
            component_table=str(payload["component_table"]),
            component_id=int(payload["component_id"]),
            quantity=int(payload["quantity"]),
            user_id=int(user.get("user_id")) if user and user.get("user_id") else None,
            from_reserved=from_reserved,
            notes=payload.get("notes")
        )
        return usage
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{repair_id}/components/reserve", status_code=status.HTTP_201_CREATED)
def reserve_component_stock(repair_id: int, payload: Dict, db: Session = Depends(get_db), user: dict = Depends(require_permission("repairs", "update"))):
    """Reservar stock para una reparación sin descontarlo del total físico."""
    required = ("component_table", "component_id", "quantity")
    for k in required:
        if k not in payload:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Missing field: {k}")

    svc = RepairService(db)
    try:
        result = svc.reserve_component(
            repair_id=repair_id,
            component_table=str(payload["component_table"]),
            component_id=int(payload["component_id"]),
            quantity=int(payload["quantity"]),
            user_id=int(user.get("user_id")) if user and user.get("user_id") else None,
            notes=payload.get("notes"),
        )
        return {"ok": True, **result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{repair_id}/components/release", status_code=status.HTTP_200_OK)
def release_component_reservation(repair_id: int, payload: Dict, db: Session = Depends(get_db), user: dict = Depends(require_permission("repairs", "update"))):
    """Liberar stock previamente reservado para una reparación."""
    required = ("component_table", "component_id", "quantity")
    for k in required:
        if k not in payload:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Missing field: {k}")

    svc = RepairService(db)
    try:
        result = svc.release_component_reservation(
            repair_id=repair_id,
            component_table=str(payload["component_table"]),
            component_id=int(payload["component_id"]),
            quantity=int(payload["quantity"]),
            user_id=int(user.get("user_id")) if user and user.get("user_id") else None,
            notes=payload.get("notes"),
        )
        return {"ok": True, **result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{repair_id}/components")
def list_component_usages(repair_id: int, db: Session = Depends(get_db), user: dict = Depends(require_permission("repairs", "read"))):
    svc = RepairService(db)
    return svc.get_component_usages(repair_id)


@router.delete("/{repair_id}/components/{usage_id}", status_code=status.HTTP_200_OK)
def remove_component_usage(repair_id: int, usage_id: int, db: Session = Depends(get_db), user: dict = Depends(require_permission("repairs", "update"))):
    """Eliminar uso de componente y devolver stock al inventario"""
    svc = RepairService(db)
    try:
        user_id = int(user.get("user_id")) if user and user.get("user_id") else None
        result = svc.remove_component_usage(usage_id=usage_id, user_id=user_id)
        return {"ok": True, "message": "Component removed and stock restored", "restored_quantity": result.get("restored_quantity", 0)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{repair_id}/notes", status_code=status.HTTP_201_CREATED)
def add_repair_note(repair_id: int, payload: Dict, db: Session = Depends(get_db), user: dict = Depends(require_permission("repairs", "update"))):
    """Agregar nota técnica o interna a una reparación"""
    note_text = payload.get("note")
    if not note_text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing field: note")

    note = RepairNote(
        repair_id=repair_id,
        user_id=int(user.get("user_id")) if user and user.get("user_id") else None,
        note=note_text,
        note_type=payload.get("note_type", "internal")
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.get("/{repair_id}/notes")
def list_repair_notes(repair_id: int, db: Session = Depends(get_db), user: dict = Depends(require_permission("repairs", "read"))):
    notes = (
        db.query(RepairNote)
        .filter(RepairNote.repair_id == repair_id)
        .order_by(RepairNote.created_at.desc())
        .all()
    )
    return notes


@router.post("/{repair_id}/photos", status_code=status.HTTP_201_CREATED)
def add_repair_photo(repair_id: int, payload: Dict, db: Session = Depends(get_db), user: dict = Depends(require_permission("repairs", "update"))):
    """Registrar URL de foto asociada a la reparación. For file uploads use `uploads` router."""
    photo_url = payload.get("photo_url")
    if not photo_url:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing field: photo_url")

    photo = RepairPhoto(
        repair_id=repair_id,
        photo_url=photo_url,
        photo_type=payload.get("photo_type", "general"),
        caption=payload.get("caption")
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


@router.get("/{repair_id}/photos")
def list_repair_photos(repair_id: int, db: Session = Depends(get_db), user: dict = Depends(require_permission("repairs", "read"))):
    photos = (
        db.query(RepairPhoto)
        .filter(RepairPhoto.repair_id == repair_id)
        .order_by(RepairPhoto.sort_order.asc(), RepairPhoto.created_at.desc())
        .all()
    )
    if settings.enable_public_uploads:
        return photos
    return [
        {
            "id": p.id,
            "photo_url": None,
            "photo_download_url": f"/api/v1/files/repair-photos/{p.id}",
            "photo_type": p.photo_type,
            "caption": p.caption,
            "created_at": p.created_at,
            "sort_order": p.sort_order,
        }
        for p in photos
    ]
