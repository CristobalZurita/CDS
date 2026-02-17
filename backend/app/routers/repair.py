"""
Router de Reparaciones
======================
Endpoints para gestión de reparaciones.
Usa permisos granulares (require_permission).
"""
from fastapi import APIRouter, Depends, HTTPException, status
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
from app.models.device_lookup import DeviceType
from app.models.client import Client
from app.models.user import User
from datetime import datetime, timedelta
import uuid
from app.core.config import settings
from app.services.email_service import EmailService
from app.services.whatsapp_service import WhatsAppService

router = APIRouter(prefix="/repairs", tags=["repairs"])

def _client_code(client_id: int) -> str:
    return f"CDS-{client_id:03d}"

def _repair_code(client_id: int, repair_id: int, suffix: int | None = None) -> str:
    base = f"{_client_code(client_id)}-OT-{repair_id:03d}"
    if suffix is not None:
        return f"{base}-{suffix:02d}"
    return base


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
    repair_code = repair.repair_number
    if client and (not repair.repair_number or repair.repair_number.startswith("R-")):
        repair_code = _repair_code(client.id, repair.id)
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
        "problem_reported": repair.problem_reported,
        "created_at": repair.created_at.isoformat() if repair.created_at else None,
        "archived_at": repair.archived_at.isoformat() if repair.archived_at else None
    }


@router.get("")
@router.get("/")
def list_repairs(
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "read"))
):
    _auto_archive_repairs(db)
    repairs = db.query(Repair).filter(Repair.archived_at.is_(None)).all()
    return [_repair_payload(repair, db) for repair in repairs]


@router.get("/archived")
def list_archived_repairs(
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "read"))
):
    _auto_archive_repairs(db)
    repairs = db.query(Repair).filter(Repair.archived_at.isnot(None)).all()
    return [_repair_payload(repair, db) for repair in repairs]


@router.post("", status_code=status.HTTP_201_CREATED)
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_repair(
    repair: Dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "create"))
):
    def _ensure_default_device_type():
        dt = db.query(DeviceType).first()
        if not dt:
            dt = DeviceType(code="generic", name="Generic", description="Autocreated")
            db.add(dt)
            db.commit()
            db.refresh(dt)
        return dt

    def _ensure_default_status():
        st = db.query(RepairStatus).filter(RepairStatus.id == 1).first()
        if not st:
            st = RepairStatus(id=1, code="ingreso", name="Ingreso", description="Autocreated")
            db.add(st)
            db.commit()
            db.refresh(st)
        return st

    def _resolve_client(client_id: int | None):
        if not client_id:
            return None
        client = db.query(Client).filter(Client.id == client_id).first()
        if client:
            return client
        user_obj = db.query(User).filter(User.id == client_id).first()
        if user_obj:
            client = Client(user_id=user_obj.id, name=user_obj.full_name, email=user_obj.email)
            db.add(client)
            db.commit()
            db.refresh(client)
            return client
        return None

    _ensure_default_status()
    device_id = repair.get("device_id")
    if not device_id:
        client = _resolve_client(repair.get("client_id"))
        if client:
            dt = _ensure_default_device_type()
            device = Device(
                client_id=client.id,
                device_type_id=dt.id,
                model=repair.get("model") or repair.get("title") or "Unknown"
            )
            db.add(device)
            db.commit()
            db.refresh(device)
            device_id = device.id

    if not device_id:
        raise HTTPException(status_code=400, detail="device_id or client_id required")

    db_repair = Repair(
        repair_number=repair.get("repair_number") or f"R-{uuid.uuid4().hex[:8]}",
        device_id=device_id,
        quote_id=repair.get("quote_id"),
        status_id=repair.get("status_id") or 1,
        assigned_to=repair.get("assigned_to"),
        problem_reported=repair.get("problem_reported") or repair.get("description") or repair.get("title") or "Sin detalle",
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
    db.add(db_repair)
    db.commit()
    db.refresh(db_repair)

    # Generar código OT correlativo (aditivo) si no se entregó un repair_number explícito
    if not repair.get("repair_number"):
        device = db.query(Device).filter(Device.id == db_repair.device_id).first()
        client_id = device.client_id if device else None
        if client_id:
            parent_id = repair.get("ot_parent_id") or repair.get("ot_base_repair_id")
            suffix = repair.get("ot_suffix")
            if parent_id:
                base_id = int(parent_id)
                base_code = _repair_code(client_id, base_id)
                parent = db.query(Repair).filter(Repair.id == base_id).first()
                if parent and parent.repair_number == base_code:
                    parent.repair_number = _repair_code(client_id, base_id, 1)
                    db.commit()
                    db.refresh(parent)
                if suffix is None:
                    like_pattern = f"{base_code}-%"
                    existing = db.query(Repair).filter(Repair.repair_number.like(like_pattern)).all()
                    suffixes = []
                    for r in existing:
                        try:
                            suffixes.append(int(r.repair_number.split("-")[-1]))
                        except Exception:
                            continue
                    suffix = (max(suffixes) + 1) if suffixes else 1
                db_repair.repair_number = _repair_code(client_id, base_id, int(suffix))
            else:
                db_repair.repair_number = _repair_code(client_id, db_repair.id, int(suffix)) if suffix is not None else _repair_code(client_id, db_repair.id)
            db.commit()
            db.refresh(db_repair)

    # Audit: repair created
    try:
        create_audit(
            event_type="repair.create",
            user_id=int(user.get("user_id")) if user and user.get("user_id") else None,
            details={"repair_id": db_repair.id},
            message="Repair created"
        )
    except Exception:
        # Non-fatal: auditing should not break main flow
        pass
    return db_repair


@router.get("/{repair_id}")
def get_repair(
    repair_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "read"))
):
    repair = db.query(Repair).filter(Repair.id == repair_id).first()
    if not repair:
        raise HTTPException(status_code=404, detail="Repair not found")
    device = db.query(Device).filter(Device.id == repair.device_id).first()
    client = db.query(Client).filter(Client.id == device.client_id).first() if device else None
    repair_code = repair.repair_number
    if client and (not repair.repair_number or repair.repair_number.startswith("R-")):
        repair_code = _repair_code(client.id, repair.id)
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
        "archived_at": repair.archived_at.isoformat() if repair.archived_at else None
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
    <style>
      .repair-photo-gallery {{
        margin-top: 8px;
      }}
      .repair-photo-thumb {{
        width: 140px;
        height: auto;
        margin: 6px;
        border-radius: 8px;
        border: 1px solid #ddd;
      }}
    </style>
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
        html_content=summary_html
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
    db_repair = db.query(Repair).get(repair_id)
    if not db_repair:
        raise HTTPException(status_code=404, detail="Repair not found")

    user_id = int(user.get("user_id")) if user and user.get("user_id") else None
    svc = RepairService(db)

    # Si hay cambio de status_id, usar el service con validación de state machine
    new_status_id = repair.get("status_id")
    if new_status_id is not None and new_status_id != db_repair.status_id:
        # Delegar al service que valida transición y emite eventos
        db_repair = svc.update_status(
            repair_id=repair_id,
            new_status_id=new_status_id,
            user_id=user_id,
            notes=repair.get("status_notes")  # Notas opcionales del cambio de estado
        )
        # Remover status_id del dict para no procesarlo de nuevo
        repair = {k: v for k, v in repair.items() if k not in ("status_id", "status_notes")}

    # Actualizar resto de campos (sin status_id)
    if repair:
        for key, value in repair.items():
            setattr(db_repair, key, value)
        db.commit()
        db.refresh(db_repair)

        # Audit: repair updated (campos no-status)
        try:
            create_audit(
                event_type="repair.update",
                user_id=user_id,
                details={"repair_id": db_repair.id, "fields": list(repair.keys())},
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
    db_repair = db.query(Repair).get(repair_id)
    if not db_repair:
        raise HTTPException(status_code=404, detail="Repair not found")
    db.delete(db_repair)
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
        usage = svc.add_component_usage(
            repair_id=repair_id,
            component_table=str(payload["component_table"]),
            component_id=int(payload["component_id"]),
            quantity=int(payload["quantity"]),
            user_id=int(user.get("user_id")) if user and user.get("user_id") else None,
            notes=payload.get("notes")
        )
        return usage
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
