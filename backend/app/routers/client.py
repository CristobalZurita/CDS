from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime
from typing import Dict, List
import json

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_permission
from app.models.user import User
from app.models.client import Client
from app.models.device import Device
from app.models.device_lookup import DeviceBrand
from app.models.repair import Repair, RepairStatus
from app.models.payment import Payment, PaymentStatus
from app.models.purchase_request import PurchaseRequest
from app.models.repair_note import RepairNote
from app.models.repair_photo import RepairPhoto
from app.core.config import settings
from app.services.logging_service import create_audit

router = APIRouter(prefix="/client", tags=["client"])


def _split_full_name(full_name: str) -> tuple[str | None, str | None]:
    parts = (full_name or "").strip().split()
    if not parts:
        return None, None
    if len(parts) == 1:
        return parts[0], None
    return parts[0], " ".join(parts[1:])


def _ensure_client(db: Session, user: User) -> Client:
    client = db.query(Client).filter(Client.user_id == user.id).first()
    if client:
        return client
    client = Client(
        user_id=user.id,
        name=user.full_name,
        email=user.email,
        phone=user.phone
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def _status_code(repair: Repair) -> str:
    if repair.status_obj and repair.status_obj.code:
        return repair.status_obj.code
    fallback = {
        1: "pending",
        2: "in_progress",
        3: "completed",
        4: "delivered",
    }
    return fallback.get(repair.status_id, "pending")


def _status_progress(code: str) -> int:
    mapping = {
        "pending_quote": 10,
        "quoted": 20,
        "approved": 30,
        "in_progress": 60,
        "waiting_parts": 35,
        "testing": 80,
        "completed": 100,
        "delivered": 100,
        "cancelled": 0,
    }
    return mapping.get(code, 10)


def _device_label(db: Session, device: Device) -> str:
    if not device:
        return "Equipo"
    brand = None
    if device.brand_other:
        brand = device.brand_other
    elif device.brand_id:
        brand_row = db.query(DeviceBrand).filter(DeviceBrand.id == device.brand_id).first()
        brand = brand_row.name if brand_row else None
    if brand:
        return f"{brand} {device.model}"
    return device.model


def _timeline_from_repair(repair: Repair) -> List[Dict]:
    timeline = []
    fields = [
        ("intake_date", "Ingreso recibido"),
        ("diagnosis_date", "Diagnóstico"),
        ("approval_date", "Aprobación"),
        ("start_date", "Reparación iniciada"),
        ("completion_date", "Reparación completada"),
        ("delivery_date", "Equipo entregado"),
    ]
    for field, label in fields:
        value = getattr(repair, field, None)
        if value:
            timeline.append({"label": label, "date": value})
    timeline.sort(key=lambda x: x["date"])
    return timeline


def _parse_payment_notes(raw_notes: str | None) -> dict:
    text = str(raw_notes or "").strip()
    if not text:
        return {}
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass
    return {"text": text}


def _build_client_purchase_request_payload(req: PurchaseRequest, latest_payment: Payment | None) -> Dict:
    total_items_amount = round(sum(
        float(item.quantity or 0) * float(item.unit_price or 0)
        for item in (req.items or [])
    ), 2)
    payment_notes = _parse_payment_notes(latest_payment.notes if latest_payment else None)
    return {
        "id": req.id,
        "status": req.status,
        "notes": req.notes,
        "repair_id": req.repair_id,
        "repair_number": req.repair.repair_number if req.repair else None,
        "items_count": len(req.items or []),
        "total_items_amount": total_items_amount,
        "requested_amount": int((latest_payment.amount or 0) if latest_payment else round(total_items_amount)),
        "payment_due_date": latest_payment.payment_due_date.isoformat() if latest_payment and latest_payment.payment_due_date else None,
        "latest_payment": (
            {
                "id": latest_payment.id,
                "status": latest_payment.status.value if isinstance(latest_payment.status, PaymentStatus) else str(latest_payment.status),
                "payment_method": latest_payment.payment_method,
                "amount": latest_payment.amount,
                "proof_path": payment_notes.get("proof_path"),
                "deposit_reference": payment_notes.get("deposit_reference"),
                "depositor_name": payment_notes.get("depositor_name"),
                "client_notes": payment_notes.get("client_notes"),
                "admin_notes": payment_notes.get("admin_notes"),
                "transaction_id": latest_payment.transaction_id,
            }
            if latest_payment
            else None
        ),
    }


@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db), user: dict = Depends(require_permission("repairs", "read"))):
    user_obj = db.query(User).filter(User.id == int(user["user_id"])).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    client = _ensure_client(db, user_obj)

    repairs = (
        db.query(Repair)
        .join(Device, Repair.device_id == Device.id)
        .filter(Device.client_id == client.id)
        .order_by(Repair.updated_at.desc())
        .all()
    )

    pending_codes = {"pending_quote", "quoted", "approved"}
    active_codes = {"in_progress", "waiting_parts", "testing"}
    completed_codes = {"completed", "delivered"}

    pending_repairs = 0
    active_repairs = 0
    completed_repairs = 0
    total_spent = 0.0
    active_list = []

    for repair in repairs:
        code = _status_code(repair)
        if code in pending_codes:
            pending_repairs += 1
        elif code in active_codes:
            active_repairs += 1
        elif code in completed_codes:
            completed_repairs += 1

        if code in completed_codes and repair.total_cost:
            total_spent += repair.total_cost

        if code in active_codes:
            active_list.append({
                "id": repair.id,
                "repair_number": repair.repair_number,
                "instrument": _device_label(db, repair.device),
                "fault": repair.problem_reported,
                "status": code,
                "date_in": repair.intake_date,
                "estimated_completion": repair.completion_date,
                "progress": _status_progress(code),
            })

    return {
        "user": {
            "id": user_obj.id,
            "email": user_obj.email,
            "full_name": user_obj.full_name,
            "phone": user_obj.phone,
            "role": user_obj.role,
        },
        "stats": {
            "pending_repairs": pending_repairs,
            "active_repairs": active_repairs,
            "completed_repairs": completed_repairs,
            "total_spent": round(total_spent, 2),
        },
        "active_repairs": active_list,
        "notifications": [],
    }


@router.get("/repairs")
def list_client_repairs(db: Session = Depends(get_db), user: dict = Depends(require_permission("repairs", "read"))):
    user_obj = db.query(User).filter(User.id == int(user["user_id"])).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    client = _ensure_client(db, user_obj)
    repairs = (
        db.query(Repair)
        .join(Device, Repair.device_id == Device.id)
        .filter(Device.client_id == client.id)
        .order_by(Repair.updated_at.desc())
        .all()
    )

    payload = []
    for repair in repairs:
        code = _status_code(repair)
        payload.append({
            "id": repair.id,
            "repair_number": repair.repair_number,
            "instrument": _device_label(db, repair.device),
            "fault": repair.problem_reported,
            "status": code,
            "date_in": repair.intake_date,
            "date_out": repair.delivery_date or repair.completion_date,
            "cost": repair.total_cost,
            "progress": _status_progress(code),
        })

    return payload


@router.get("/repairs/{repair_id}/timeline")
def get_repair_timeline(repair_id: int, db: Session = Depends(get_db), user: dict = Depends(require_permission("repairs", "read"))):
    user_obj = db.query(User).filter(User.id == int(user["user_id"])).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    client = _ensure_client(db, user_obj)
    repair = (
        db.query(Repair)
        .join(Device, Repair.device_id == Device.id)
        .filter(Device.client_id == client.id, Repair.id == repair_id)
        .first()
    )
    if not repair:
        raise HTTPException(status_code=404, detail="Reparación no encontrada")

    return {
        "repair_id": repair.id,
        "repair_number": repair.repair_number,
        "status": _status_code(repair),
        "timeline": _timeline_from_repair(repair),
    }


@router.get("/repairs/{repair_id}/details")
def get_repair_details(repair_id: int, db: Session = Depends(get_db), user: dict = Depends(require_permission("repairs", "read"))):
    user_obj = db.query(User).filter(User.id == int(user["user_id"])).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    client = _ensure_client(db, user_obj)
    repair = (
        db.query(Repair)
        .join(Device, Repair.device_id == Device.id)
        .filter(Device.client_id == client.id, Repair.id == repair_id)
        .first()
    )
    if not repair:
        raise HTTPException(status_code=404, detail="Reparación no encontrada")

    photos = (
        db.query(RepairPhoto)
        .filter(RepairPhoto.repair_id == repair.id, RepairPhoto.visible_to_client == 1)
        .order_by(RepairPhoto.sort_order.asc(), RepairPhoto.created_at.desc())
        .all()
    )
    notes = (
        db.query(RepairNote)
        .filter(RepairNote.repair_id == repair.id, RepairNote.note_type != "internal")
        .order_by(RepairNote.created_at.desc())
        .all()
    )

    return {
        "repair": {
            "id": repair.id,
            "repair_number": repair.repair_number,
            "instrument": _device_label(db, repair.device),
            "status": _status_code(repair),
            "problem_reported": repair.problem_reported,
            "diagnosis": repair.diagnosis,
            "work_performed": repair.work_performed,
            "total_cost": repair.total_cost,
        },
        "timeline": _timeline_from_repair(repair),
        "photos": [
            {
                "id": p.id,
                "photo_url": p.photo_url if settings.enable_public_uploads else None,
                "photo_download_url": f"/api/v1/files/repair-photos/{p.id}" if not settings.enable_public_uploads else None,
                "photo_type": p.photo_type,
                "caption": p.caption,
                "created_at": p.created_at,
            }
            for p in photos
        ],
        "notes": [
            {
                "id": n.id,
                "note": n.note,
                "note_type": n.note_type,
                "created_at": n.created_at,
            }
            for n in notes
        ],
    }


@router.get("/profile")
def get_profile(db: Session = Depends(get_db), user: dict = Depends(require_permission("repairs", "read"))):
    user_obj = db.query(User).filter(User.id == int(user["user_id"])).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    client = _ensure_client(db, user_obj)

    return {
        "email": user_obj.email,
        "full_name": user_obj.full_name,
        "phone": user_obj.phone,
        "address": client.address,
        "member_since": user_obj.created_at,
        "stats": {
            "total_repairs": client.total_repairs,
            "total_spent": client.total_spent,
        },
    }


@router.put("/profile")
def update_profile(payload: Dict, db: Session = Depends(get_db), user: dict = Depends(require_permission("repairs", "read"))):
    user_obj = db.query(User).filter(User.id == int(user["user_id"])).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    client = _ensure_client(db, user_obj)

    email = payload.get("email")
    full_name = payload.get("full_name")
    phone = payload.get("phone")
    address = payload.get("address")

    if email and email != user_obj.email:
        existing = db.query(User).filter(User.email == email).first()
        if existing and existing.id != user_obj.id:
            raise HTTPException(status_code=400, detail="Email ya registrado")
        user_obj.email = email
        client.email = email

    if full_name is not None:
        first_name, last_name = _split_full_name(full_name)
        user_obj.first_name = first_name
        user_obj.last_name = last_name
        client.name = full_name or client.name

    if phone is not None:
        user_obj.phone = phone
        client.phone = phone

    if address is not None:
        client.address = address

    db.add(user_obj)
    db.add(client)
    db.commit()
    db.refresh(user_obj)
    db.refresh(client)

    return {
        "email": user_obj.email,
        "full_name": user_obj.full_name,
        "phone": user_obj.phone,
        "address": client.address,
        "member_since": user_obj.created_at,
        "stats": {
            "total_repairs": client.total_repairs,
            "total_spent": client.total_spent,
        },
    }


@router.get("/purchase-requests")
def list_client_purchase_requests(
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "read")),
):
    user_obj = db.query(User).filter(User.id == int(user["user_id"])).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    client = _ensure_client(db, user_obj)

    repair_ids = [
        row[0]
        for row in (
            db.query(Repair.id)
            .join(Device, Repair.device_id == Device.id)
            .filter(Device.client_id == client.id)
            .all()
        )
    ]

    query = db.query(PurchaseRequest)
    if repair_ids:
        query = query.filter(
            or_(
                PurchaseRequest.client_id == client.id,
                PurchaseRequest.repair_id.in_(repair_ids),
            )
        )
    else:
        query = query.filter(PurchaseRequest.client_id == client.id)

    requests = query.order_by(PurchaseRequest.updated_at.desc()).all()
    request_ids = [req.id for req in requests]

    latest_by_request: Dict[int, Payment] = {}
    if request_ids:
        payments = (
            db.query(Payment)
            .filter(Payment.purchase_request_id.in_(request_ids))
            .order_by(Payment.id.desc())
            .all()
        )
        for payment in payments:
            request_id = int(payment.purchase_request_id or 0)
            if request_id > 0 and request_id not in latest_by_request:
                latest_by_request[request_id] = payment

    return [
        _build_client_purchase_request_payload(req, latest_by_request.get(req.id))
        for req in requests
    ]


@router.post("/purchase-requests/{request_id}/deposit-proof")
def submit_client_deposit_proof(
    request_id: int,
    payload: Dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "read")),
):
    user_obj = db.query(User).filter(User.id == int(user["user_id"])).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    client = _ensure_client(db, user_obj)
    req = db.query(PurchaseRequest).filter(PurchaseRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Solicitud de compra no encontrada")

    allowed_client_ids = {client.id}
    if req.repair_id:
        repair = db.query(Repair).filter(Repair.id == req.repair_id).first()
        if repair:
            device = db.query(Device).filter(Device.id == repair.device_id).first()
            if device and device.client_id:
                allowed_client_ids.add(int(device.client_id))
    if req.client_id and int(req.client_id) not in allowed_client_ids:
        raise HTTPException(status_code=403, detail="No autorizado para esta solicitud de compra")
    if req.client_id is None and client.id not in allowed_client_ids:
        raise HTTPException(status_code=403, detail="No autorizado para esta solicitud de compra")

    if req.status not in {"pending_payment", "requested", "proof_submitted"}:
        raise HTTPException(status_code=400, detail="La solicitud no está en estado de pago")

    payment = (
        db.query(Payment)
        .filter(
            Payment.purchase_request_id == req.id,
            Payment.status == PaymentStatus.PENDING,
        )
        .order_by(Payment.id.desc())
        .first()
    )

    requested_amount = payload.get("amount")
    if requested_amount is None:
        requested_amount = int(round(sum(
            float(item.quantity or 0) * float(item.unit_price or 0)
            for item in (req.items or [])
        )))
    amount = int(round(float(requested_amount)))
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Monto inválido")

    if not payment:
        payment = Payment(
            user_id=user_obj.id,
            repair_id=req.repair_id,
            purchase_request_id=req.id,
            amount=amount,
            payment_method="transfer",
            status=PaymentStatus.PENDING,
            transaction_id=f"DEP-{req.id}-{int(datetime.utcnow().timestamp())}",
            payment_processor="manual",
            currency="CLP",
        )
        db.add(payment)
        db.flush()
    else:
        payment.amount = amount
        if not payment.transaction_id:
            payment.transaction_id = f"DEP-{req.id}-{int(datetime.utcnow().timestamp())}"

    payment_notes = _parse_payment_notes(payment.notes)
    payment_notes["proof_path"] = payload.get("proof_path")
    payment_notes["deposit_reference"] = payload.get("deposit_reference")
    payment_notes["depositor_name"] = payload.get("depositor_name") or user_obj.full_name
    payment_notes["client_notes"] = payload.get("client_notes")
    payment.notes = json.dumps(payment_notes, ensure_ascii=False)

    deposited_at = payload.get("deposited_at")
    if deposited_at:
        try:
            payment.payment_date = datetime.fromisoformat(str(deposited_at))
        except Exception:
            payment.payment_date = datetime.utcnow()
    else:
        payment.payment_date = datetime.utcnow()

    req.status = "proof_submitted"
    db.commit()
    db.refresh(req)
    db.refresh(payment)

    try:
        create_audit(
            event_type="purchase_request.deposit_proof_submitted",
            user_id=user_obj.id,
            details={
                "request_id": req.id,
                "payment_id": payment.id,
                "amount": payment.amount,
                "proof_path": payload.get("proof_path"),
            },
            message=f"Deposit proof submitted for purchase request #{req.id}",
        )
    except Exception:
        pass

    return {
        "ok": True,
        "request": _build_client_purchase_request_payload(req, payment),
    }
