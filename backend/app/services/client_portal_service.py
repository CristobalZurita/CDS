from __future__ import annotations

import json
from datetime import datetime
from typing import Dict, List

from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.client import Client
from app.models.category import Category
from app.models.device import Device
from app.models.device_lookup import DeviceBrand
from app.models.inventory import Product
from app.models.payment import Payment, PaymentStatus
from app.models.purchase_request import PurchaseRequest, PurchaseRequestItem
from app.models.repair import Repair
from app.models.repair_component_usage import RepairComponentUsage
from app.models.repair_intake_sheet import RepairIntakeSheet
from app.models.repair_note import RepairNote
from app.models.repair_photo import RepairPhoto
from app.models.stock import Stock
from app.models.user import User
from app.services.inventory_catalog_service import store_visible_from_meta
from app.services.logging_service import create_audit
from app.services.purchase_request_service import _apply_request_stock_state
from app.services.repair_helpers import (
    resolved_repair_code as _resolved_repair_code,
    safe_pdf_filename as _safe_pdf_filename,
)
from app.services.user_helpers import split_full_name as _split_full_name


_STATUS_ALIASES = {
    "pending": "ingreso",
    "pending_quote": "ingreso",
    "quoted": "presupuesto",
    "approved": "aprobado",
    "in_progress": "en_trabajo",
    "in-progress": "en_trabajo",
    "waiting_parts": "en_trabajo",
    "waiting": "en_trabajo",
    "testing": "listo",
    "completed": "entregado",
    "delivered": "entregado",
    "cancelled": "rechazado",
    "ingreso": "ingreso",
    "diagnostico": "diagnostico",
    "presupuesto": "presupuesto",
    "aprobado": "aprobado",
    "en_trabajo": "en_trabajo",
    "listo": "listo",
    "entregado": "entregado",
    "noventena": "noventena",
    "archivado": "archivado",
    "rechazado": "rechazado",
}


def ensure_client(db: Session, user: User) -> Client:
    client = db.query(Client).filter(Client.user_id == user.id).first()
    if client:
        return client
    client = Client(
        user_id=user.id,
        name=user.full_name,
        email=user.email,
        phone=user.phone,
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def get_client_user_or_404(db: Session, user_id: int) -> User:
    user_obj = db.query(User).filter(User.id == int(user_id)).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user_obj


def status_code(repair: Repair) -> str:
    if repair.status_obj and repair.status_obj.code:
        return repair.status_obj.code
    fallback = {
        1: "ingreso",
        2: "diagnostico",
        3: "presupuesto",
        4: "aprobado",
        5: "en_trabajo",
        6: "listo",
        7: "entregado",
        8: "noventena",
        9: "archivado",
        10: "rechazado",
    }
    return fallback.get(repair.status_id, "ingreso")


def normalize_status_code(code: str | None) -> str:
    value = str(code or "").strip().lower()
    return _STATUS_ALIASES.get(value, value or "ingreso")


def status_progress(code: str) -> int:
    normalized = normalize_status_code(code)
    mapping = {
        "ingreso": 10,
        "diagnostico": 20,
        "presupuesto": 30,
        "aprobado": 40,
        "en_trabajo": 60,
        "listo": 80,
        "entregado": 100,
        "noventena": 100,
        "archivado": 100,
        "rechazado": 0,
    }
    return mapping.get(normalized, 10)


def device_label(db: Session, device: Device | None) -> str:
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


def timeline_from_repair(repair: Repair) -> List[Dict]:
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


def parse_payment_notes(raw_notes: str | None) -> dict:
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


def parse_product_meta(description: str | None) -> dict:
    text = str(description or "").strip()
    if not text.startswith("{"):
        return {}
    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


def product_store_enabled(product: Product) -> bool:
    meta = parse_product_meta(product.description)
    category_name = None
    if getattr(product, "category", None):
        category_name = product.category.name
    return store_visible_from_meta(meta, product, category_name)


def product_sellable_stock(db: Session, product: Product) -> int:
    stock = (
        db.query(Stock)
        .filter(
            Stock.component_table == "products",
            Stock.component_id == product.id,
        )
        .first()
    )
    available_qty = int(stock.available_quantity if stock else product.quantity or 0)
    min_stock = int(stock.minimum_stock if stock else product.min_quantity or 0)
    return max(available_qty - min_stock, 0)


def build_client_purchase_request_payload(
    req: PurchaseRequest,
    latest_payment: Payment | None,
    client_id: int | None = None,
) -> Dict:
    total_items_amount = round(
        sum(float(item.quantity or 0) * float(item.unit_price or 0) for item in (req.items or [])),
        2,
    )
    payment_notes = parse_payment_notes(latest_payment.notes if latest_payment else None)
    resolved_client_id = int(client_id or req.client_id or 0) or None
    resolved_repair_code = _resolved_repair_code(req.repair, resolved_client_id)
    return {
        "id": req.id,
        "status": req.status,
        "notes": req.notes,
        "repair_id": req.repair_id,
        "repair_number": req.repair.repair_number if req.repair else None,
        "repair_code": resolved_repair_code,
        "items_count": len(req.items or []),
        "total_items_amount": total_items_amount,
        "requested_amount": int((latest_payment.amount or 0) if latest_payment else round(total_items_amount)),
        "payment_due_date": latest_payment.payment_due_date.isoformat()
        if latest_payment and latest_payment.payment_due_date
        else None,
        "latest_payment": (
            {
                "id": latest_payment.id,
                "status": latest_payment.status.value
                if isinstance(latest_payment.status, PaymentStatus)
                else str(latest_payment.status),
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


def get_dashboard_payload(db: Session, user_id: int) -> dict:
    user_obj = get_client_user_or_404(db, user_id)
    client = ensure_client(db, user_obj)

    repairs = (
        db.query(Repair)
        .join(Device, Repair.device_id == Device.id)
        .filter(Device.client_id == client.id)
        .order_by(Repair.updated_at.desc())
        .all()
    )

    pending_codes = {"ingreso", "diagnostico", "presupuesto"}
    active_codes = {"aprobado", "en_trabajo", "listo"}
    completed_codes = {"entregado", "noventena", "archivado"}

    pending_repairs = 0
    active_repairs = 0
    completed_repairs = 0
    total_spent = 0.0
    active_list = []
    repair_ids = []

    for repair in repairs:
        repair_ids.append(int(repair.id))
        raw_code = status_code(repair)
        normalized_code = normalize_status_code(raw_code)
        repair_code = _resolved_repair_code(repair, client.id)
        if normalized_code in pending_codes:
            pending_repairs += 1
        elif normalized_code in active_codes:
            active_repairs += 1
        elif normalized_code in completed_codes:
            completed_repairs += 1

        if normalized_code in completed_codes and repair.total_cost:
            total_spent += repair.total_cost

        if normalized_code in active_codes:
            active_list.append(
                {
                    "id": repair.id,
                    "repair_number": repair.repair_number,
                    "repair_code": repair_code,
                    "instrument": device_label(db, repair.device),
                    "fault": repair.problem_reported,
                    "status": raw_code,
                    "status_normalized": normalized_code,
                    "date_in": repair.intake_date,
                    "estimated_completion": repair.completion_date,
                    "progress": status_progress(normalized_code),
                }
            )

    open_payment_statuses = {"requested", "pending_payment", "proof_submitted"}
    purchase_query = db.query(PurchaseRequest)
    if repair_ids:
        purchase_query = purchase_query.filter(
            or_(
                PurchaseRequest.client_id == client.id,
                PurchaseRequest.repair_id.in_(repair_ids),
            )
        )
    else:
        purchase_query = purchase_query.filter(PurchaseRequest.client_id == client.id)

    open_payment_requests = (
        purchase_query
        .filter(PurchaseRequest.status.in_(open_payment_statuses))
        .order_by(PurchaseRequest.updated_at.desc())
        .limit(8)
        .all()
    )

    notifications = []
    for req in open_payment_requests:
        latest_payment = (
            db.query(Payment)
            .filter(Payment.purchase_request_id == req.id)
            .order_by(Payment.id.desc())
            .first()
        )
        due_text = ""
        if latest_payment and latest_payment.payment_due_date:
            due_text = f" (vence {latest_payment.payment_due_date.strftime('%d-%m-%Y')})"

        if req.status in {"requested", "pending_payment"}:
            message = f"Tienes un pago OT pendiente para la solicitud #{req.id}{due_text}"
            notif_type = "warning"
        else:
            message = f"Tu comprobante OT #{req.id} fue recibido y está en validación"
            notif_type = "info"

        notifications.append(
            {
                "id": f"ot-payment-{req.id}",
                "type": notif_type,
                "message": message,
                "date": req.updated_at or datetime.utcnow(),
            }
        )

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
            "pending_ot_payments": len(open_payment_requests),
        },
        "active_repairs": active_list,
        "notifications": notifications,
    }


def list_client_repairs_payload(db: Session, user_id: int) -> list[dict]:
    user_obj = get_client_user_or_404(db, user_id)
    client = ensure_client(db, user_obj)
    repairs = (
        db.query(Repair)
        .join(Device, Repair.device_id == Device.id)
        .filter(Device.client_id == client.id)
        .order_by(Repair.updated_at.desc())
        .all()
    )

    payload = []
    for repair in repairs:
        raw_code = status_code(repair)
        normalized_code = normalize_status_code(raw_code)
        repair_code = _resolved_repair_code(repair, client.id)
        payload.append(
            {
                "id": repair.id,
                "repair_number": repair.repair_number,
                "repair_code": repair_code,
                "instrument": device_label(db, repair.device),
                "fault": repair.problem_reported,
                "status": raw_code,
                "status_normalized": normalized_code,
                "date_in": repair.intake_date,
                "date_out": repair.delivery_date or repair.completion_date,
                "cost": repair.total_cost,
                "progress": status_progress(normalized_code),
            }
        )
    return payload


def _get_client_repair_or_404(db: Session, client_id: int, repair_id: int) -> Repair:
    repair = (
        db.query(Repair)
        .join(Device, Repair.device_id == Device.id)
        .filter(Device.client_id == client_id, Repair.id == repair_id)
        .first()
    )
    if not repair:
        raise HTTPException(status_code=404, detail="Reparación no encontrada")
    return repair


def get_repair_timeline_payload(db: Session, user_id: int, repair_id: int) -> dict:
    user_obj = get_client_user_or_404(db, user_id)
    client = ensure_client(db, user_obj)
    repair = _get_client_repair_or_404(db, client.id, repair_id)
    raw_code = status_code(repair)
    return {
        "repair_id": repair.id,
        "repair_number": repair.repair_number,
        "repair_code": _resolved_repair_code(repair, client.id),
        "status": raw_code,
        "status_normalized": normalize_status_code(raw_code),
        "timeline": timeline_from_repair(repair),
    }


def get_repair_details_payload(db: Session, user_id: int, repair_id: int) -> dict:
    user_obj = get_client_user_or_404(db, user_id)
    client = ensure_client(db, user_obj)
    repair = _get_client_repair_or_404(db, client.id, repair_id)

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

    raw_code = status_code(repair)
    normalized = normalize_status_code(raw_code)
    return {
        "repair": {
            "id": repair.id,
            "repair_number": repair.repair_number,
            "repair_code": _resolved_repair_code(repair, client.id),
            "instrument": device_label(db, repair.device),
            "status": raw_code,
            "status_normalized": normalized,
            "problem_reported": repair.problem_reported,
            "diagnosis": repair.diagnosis,
            "work_performed": repair.work_performed,
            "total_cost": repair.total_cost,
        },
        "timeline": timeline_from_repair(repair),
        "photos": [
            {
                "id": photo.id,
                "photo_url": photo.photo_url if settings.enable_public_uploads else None,
                "photo_download_url": f"/api/v1/files/repair-photos/{photo.id}"
                if not settings.enable_public_uploads
                else None,
                "photo_type": photo.photo_type,
                "caption": photo.caption,
                "created_at": photo.created_at,
            }
            for photo in photos
        ],
        "notes": [
            {
                "id": note.id,
                "note": note.note,
                "note_type": note.note_type,
                "created_at": note.created_at,
            }
            for note in notes
        ],
    }


def build_client_closure_pdf_payload(
    db: Session,
    user_id: int,
    repair_id: int,
) -> tuple[dict, str, int]:
    user_obj = get_client_user_or_404(db, user_id)
    client = ensure_client(db, user_obj)
    repair = _get_client_repair_or_404(db, client.id, repair_id)

    notes = (
        db.query(RepairNote)
        .filter(RepairNote.repair_id == repair.id, RepairNote.note_type != "internal")
        .order_by(RepairNote.created_at.asc())
        .all()
    )
    components = (
        db.query(RepairComponentUsage)
        .filter(RepairComponentUsage.repair_id == repair.id)
        .order_by(RepairComponentUsage.created_at.asc())
        .all()
    )
    photos_count = (
        db.query(RepairPhoto)
        .filter(RepairPhoto.repair_id == repair.id, RepairPhoto.visible_to_client == 1)
        .count()
    )
    intake_sheet = (
        db.query(RepairIntakeSheet)
        .filter(RepairIntakeSheet.repair_id == repair.id)
        .first()
    )
    resolved_repair_code = _resolved_repair_code(repair, client.id)

    payload = {
        "repair_id": repair.id,
        "repair_number": repair.repair_number,
        "repair_code": resolved_repair_code,
        "status_id": repair.status_id,
        "status_name": status_code(repair),
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
        "client_name": client.name,
        "client_email": client.email,
        "client_phone": client.phone,
        "device_model": repair.device.model if repair.device else None,
        "device_serial": repair.device.serial_number if repair.device else None,
        "components": [
            {
                "component_table": component.component_table,
                "component_id": component.component_id,
                "quantity": component.quantity,
                "unit_cost": component.unit_cost or 0,
                "total_cost": component.total_cost,
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
        "intake_sheet": (
            {
                "client_code": intake_sheet.client_code,
                "ot_code": intake_sheet.ot_code,
                "instrument_code": intake_sheet.instrument_code,
                "equipment_type": intake_sheet.equipment_type,
                "requested_service_type": intake_sheet.requested_service_type,
                "repair_tariff": intake_sheet.repair_tariff,
                "material_tariff": intake_sheet.material_tariff,
                "estimated_repair_time": intake_sheet.estimated_repair_time,
                "estimated_completion_date": intake_sheet.estimated_completion_date,
                "annotations": intake_sheet.annotations,
            }
            if intake_sheet
            else None
        ),
    }
    safe_code = _safe_pdf_filename(
        resolved_repair_code or repair.repair_number or f"OT_{repair.id}"
    )
    filename = f"CIERRE_CLIENTE_{safe_code}.pdf"
    return payload, filename, user_obj.id


def audit_client_closure_pdf_download(repair_id: int, filename: str, user_id: int) -> None:
    try:
        create_audit(
            event_type="repair.closure_pdf.client_download",
            user_id=user_id,
            details={"repair_id": repair_id, "filename": filename},
            message=f"Client downloaded closure PDF for repair #{repair_id}",
        )
    except Exception:
        pass


def get_profile_payload(db: Session, user_id: int) -> dict:
    user_obj = get_client_user_or_404(db, user_id)
    client = ensure_client(db, user_obj)
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


def update_profile_payload(db: Session, user_id: int, payload: Dict) -> dict:
    user_obj = get_client_user_or_404(db, user_id)
    client = ensure_client(db, user_obj)

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


def list_client_purchase_requests_payload(db: Session, user_id: int) -> list[Dict]:
    user_obj = get_client_user_or_404(db, user_id)
    client = ensure_client(db, user_obj)

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
        build_client_purchase_request_payload(req, latest_by_request.get(req.id), client.id)
        for req in requests
    ]


def create_store_purchase_request_record(db: Session, user_id: int, payload: Dict) -> dict:
    user_obj = get_client_user_or_404(db, user_id)
    client = ensure_client(db, user_obj)
    raw_items = payload.get("items") or []
    if not isinstance(raw_items, list) or not raw_items:
        raise HTTPException(status_code=400, detail="Debes enviar al menos un producto")

    shipping_label = str(
        payload.get("shipping_label") or payload.get("shipping_name") or "Retiro en taller"
    ).strip()
    shipping_key = str(payload.get("shipping_key") or "pickup").strip() or "pickup"
    client_note = str(payload.get("notes") or "").strip()

    note_parts = [
        "Solicitud creada desde tienda web",
        f"Despacho: {shipping_label}",
        f"Canal: {shipping_key}",
    ]
    if client_note:
        note_parts.append(f"Nota cliente: {client_note}")

    req = PurchaseRequest(
        client_id=client.id,
        repair_id=None,
        created_by=user_obj.id,
        status="requested",
        notes=" | ".join(note_parts),
    )
    db.add(req)
    db.flush()

    total_items = 0
    pending_availability = []
    for raw_item in raw_items:
        product_id = int(raw_item.get("product_id") or 0)
        quantity = int(raw_item.get("quantity") or 0)
        if product_id <= 0 or quantity <= 0:
            raise HTTPException(status_code=400, detail="Producto o cantidad inválida")

        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Producto no encontrado: {product_id}")
        if not getattr(product, "category", None):
            product.category = db.query(Category).filter(Category.id == product.category_id).first()
        if not product_store_enabled(product):
            raise HTTPException(
                status_code=400,
                detail=f"Producto no disponible para tienda: {product.sku}",
            )

        sellable_stock = product_sellable_stock(db, product)
        if sellable_stock < quantity:
            pending_availability.append(f"{product.sku} ({sellable_stock} vendible)")

        unit_price = float(raw_item.get("unit_price") or product.price or 0)
        db.add(
            PurchaseRequestItem(
                request_id=req.id,
                product_id=product.id,
                sku=product.sku,
                name=product.name,
                quantity=quantity,
                unit_price=unit_price,
                status="suggested",
            )
        )
        total_items += quantity

    if pending_availability:
        note_parts.append("Revisar disponibilidad taller: " + ", ".join(pending_availability[:6]))
        req.notes = " | ".join(note_parts)

    db.flush()
    _apply_request_stock_state(
        db,
        req,
        previous_status="draft",
        next_status=req.status,
        user_id=user_obj.id,
    )
    db.commit()
    db.refresh(req)

    try:
        create_audit(
            event_type="store.purchase_request_created",
            user_id=user_obj.id,
            details={
                "request_id": req.id,
                "client_id": client.id,
                "items": total_items,
                "shipping": shipping_key,
            },
            message=f"Store purchase request #{req.id} created",
        )
    except Exception:
        pass

    return {
        "ok": True,
        "request": build_client_purchase_request_payload(req, None, client.id),
    }


def submit_client_deposit_proof_record(
    db: Session,
    user_id: int,
    request_id: int,
    payload: Dict,
) -> dict:
    user_obj = get_client_user_or_404(db, user_id)
    client = ensure_client(db, user_obj)
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
        requested_amount = int(
            round(sum(float(item.quantity or 0) * float(item.unit_price or 0) for item in (req.items or [])))
        )
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

    payment_notes = parse_payment_notes(payment.notes)
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
        "request": build_client_purchase_request_payload(req, payment, client.id),
    }
