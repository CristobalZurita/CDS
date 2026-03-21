from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.payment import Payment, PaymentStatus
from app.models.purchase_request import PurchaseRequest, PurchaseRequestItem
from app.models.stock import Stock
from app.models.stock_movement import StockMovement
from app.schemas.purchase_request import PurchaseRequestCreate
from app.services.logging_service import create_audit
from app.services.repair_helpers import resolved_repair_code as _resolved_repair_code_shared

LEGACY_STATUSES = {
    "draft",
    "suggested",
    "approved",
    "purchased",
    "received",
    "cancelled",
}

FLOW_STATUSES = {
    "requested",
    "pending_payment",
    "proof_submitted",
    "paid_client",
    "purchased_admin",
    "received",
    "applied_ot",
    "cancelled",
}

VALID_STATUSES = LEGACY_STATUSES | FLOW_STATUSES
RESERVE_PHASE_STATUSES = {
    "requested",
    "pending_payment",
    "proof_submitted",
    "paid_client",
    "purchased_admin",
}
FULFILLED_PHASE_STATUSES = {
    "received",
    "applied_ot",
}


def _normalize_status(raw: str | None, fallback: str = "draft") -> str:
    value = str(raw or "").strip().lower()
    if not value:
        return fallback
    if value not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid purchase request status: {value}")
    return value


def _stock_phase(raw: str | None) -> str:
    value = _normalize_status(raw, fallback="draft")
    if value in FULFILLED_PHASE_STATUSES:
        return "fulfilled"
    if value in RESERVE_PHASE_STATUSES:
        return "reserved"
    return "idle"


def _request_total(req: PurchaseRequest) -> float:
    total = 0.0
    for item in req.items or []:
        total += float(item.quantity or 0) * float(item.unit_price or 0)
    return round(total, 2)


def _request_shipping_snapshot(req: PurchaseRequest) -> dict[str, Any] | None:
    raw_notes = str(req.notes or "").strip()
    if not raw_notes:
        return None

    snapshot: dict[str, Any] = {"raw_notes": raw_notes}
    for part in raw_notes.split("|"):
        text = str(part or "").strip()
        lowered = text.lower()
        if lowered.startswith("despacho:"):
            snapshot["shipping_label"] = text.split(":", 1)[1].strip() or None
        elif lowered.startswith("canal:"):
            snapshot["shipping_channel"] = text.split(":", 1)[1].strip() or None
        elif lowered.startswith("nota cliente:"):
            snapshot["client_note"] = text.split(":", 1)[1].strip() or None

    return {key: value for key, value in snapshot.items() if value not in (None, "")}


def _request_items_snapshot(req: PurchaseRequest) -> list[dict[str, Any]]:
    payload: list[dict[str, Any]] = []
    for item in req.items or []:
        payload.append(
            {
                "id": item.id,
                "product_id": item.product_id,
                "sku": item.sku,
                "name": item.name,
                "quantity": int(item.quantity or 0),
                "reserved_quantity": _request_item_reserved(item),
                "unit_price": float(item.unit_price or 0),
                "status": item.status,
            }
        )
    return payload


def _request_item_reserved(item: PurchaseRequestItem) -> int:
    return max(int(getattr(item, "reserved_quantity", 0) or 0), 0)


def _request_item_label(item: PurchaseRequestItem) -> str:
    value = str(item.sku or item.name or f"product:{item.product_id or 'n/a'}").strip()
    return value or "producto"


def _request_item_stock(db: Session, item: PurchaseRequestItem) -> Stock | None:
    product_id = int(item.product_id or 0)
    if product_id <= 0:
        return None
    return (
        db.query(Stock)
        .filter(
            Stock.component_table == "products",
            Stock.component_id == product_id,
        )
        .first()
    )


def _sellable_stock_including_item(stock: Stock, item: PurchaseRequestItem) -> int:
    current_reserved = _request_item_reserved(item)
    minimum_stock = max(int(stock.minimum_stock or 0), 0)
    available_including_self = max(int(stock.available_quantity or 0), 0) + current_reserved
    return max(available_including_self - minimum_stock, 0)


def _desired_reserved_quantity(stock: Stock, item: PurchaseRequestItem) -> int:
    requested_qty = max(int(item.quantity or 0), 0)
    sellable_qty = _sellable_stock_including_item(stock, item)
    return min(requested_qty, sellable_qty)


def _append_stock_movement(
    db: Session,
    *,
    stock: Stock,
    req: PurchaseRequest,
    item: PurchaseRequestItem,
    movement_type: str,
    quantity: int,
    user_id: int | None,
    status_label: str | None = None,
) -> None:
    qty = max(int(quantity or 0), 0)
    if qty <= 0:
        return

    suffix = f" / estado {status_label}" if status_label else ""
    db.add(
        StockMovement(
            stock_id=stock.id,
            movement_type=movement_type,
            quantity=qty,
            repair_id=req.repair_id,
            notes=f"Solicitud compra #{req.id} / {_request_item_label(item)}{suffix}",
            performed_by=user_id,
        )
    )


def _align_request_reservations(db: Session, req: PurchaseRequest, user_id: int | None) -> None:
    for item in req.items or []:
        stock = _request_item_stock(db, item)
        current_reserved = _request_item_reserved(item)

        if not stock:
            if current_reserved > 0:
                item.reserved_quantity = 0
            continue

        desired_reserved = _desired_reserved_quantity(stock, item)
        if desired_reserved == current_reserved:
            continue

        if desired_reserved > current_reserved:
            reserve_delta = desired_reserved - current_reserved
            stock.quantity_reserved = int(stock.quantity_reserved or 0) + reserve_delta
            item.reserved_quantity = desired_reserved
            stock.updated_at = datetime.utcnow()
            _append_stock_movement(
                db,
                stock=stock,
                req=req,
                item=item,
                movement_type="RESERVE",
                quantity=reserve_delta,
                user_id=user_id,
                status_label=req.status,
            )
            continue

        release_delta = current_reserved - desired_reserved
        stock.quantity_reserved = max(int(stock.quantity_reserved or 0) - release_delta, 0)
        item.reserved_quantity = desired_reserved
        stock.updated_at = datetime.utcnow()
        _append_stock_movement(
            db,
            stock=stock,
            req=req,
            item=item,
            movement_type="UNRESERVE",
            quantity=release_delta,
            user_id=user_id,
            status_label=req.status,
        )


def _release_request_reservations(db: Session, req: PurchaseRequest, user_id: int | None) -> None:
    for item in req.items or []:
        stock = _request_item_stock(db, item)
        reserved_qty = _request_item_reserved(item)
        if reserved_qty <= 0:
            continue

        if stock:
            stock.quantity_reserved = max(int(stock.quantity_reserved or 0) - reserved_qty, 0)
            stock.updated_at = datetime.utcnow()
            _append_stock_movement(
                db,
                stock=stock,
                req=req,
                item=item,
                movement_type="UNRESERVE",
                quantity=reserved_qty,
                user_id=user_id,
                status_label=req.status,
            )
        item.reserved_quantity = 0


def _consume_request_reservations(
    db: Session,
    req: PurchaseRequest,
    user_id: int | None,
    target_status: str,
) -> None:
    for item in req.items or []:
        stock = _request_item_stock(db, item)
        reserved_qty = _request_item_reserved(item)
        if reserved_qty <= 0:
            continue

        if not stock:
            item.reserved_quantity = 0
            continue

        stock_reserved = max(int(stock.quantity_reserved or 0), 0)
        stock_quantity = max(int(stock.quantity or 0), 0)
        consume_qty = min(reserved_qty, stock_reserved, stock_quantity)
        if consume_qty <= 0:
            continue

        stock.quantity = stock_quantity - consume_qty
        stock.quantity_reserved = stock_reserved - consume_qty
        stock.updated_at = datetime.utcnow()
        item.reserved_quantity = max(reserved_qty - consume_qty, 0)
        _append_stock_movement(
            db,
            stock=stock,
            req=req,
            item=item,
            movement_type="OUT_RESERVED",
            quantity=consume_qty,
            user_id=user_id,
            status_label=target_status,
        )


def _apply_request_stock_state(
    db: Session,
    req: PurchaseRequest,
    previous_status: str | None,
    next_status: str | None,
    user_id: int | None,
) -> None:
    old_phase = _stock_phase(previous_status)
    new_phase = _stock_phase(next_status)

    if new_phase == "reserved":
        _align_request_reservations(db, req, user_id)
        return

    if new_phase == "fulfilled":
        if old_phase != "fulfilled":
            _align_request_reservations(db, req, user_id)
            _consume_request_reservations(db, req, user_id, _normalize_status(next_status))
        return

    if old_phase == "reserved":
        _release_request_reservations(db, req, user_id)


def _parse_notes_metadata(raw_notes: str | None) -> dict:
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


def _latest_request_payment(db: Session, request_id: int) -> Payment | None:
    return (
        db.query(Payment)
        .filter(Payment.purchase_request_id == request_id)
        .order_by(Payment.id.desc())
        .first()
    )


def _resolved_repair_code(req: PurchaseRequest) -> str | None:
    return _resolved_repair_code_shared(req.repair, int(req.client_id or 0) or None)


def _serialize_request(db: Session, req: PurchaseRequest) -> dict:
    latest_payment = _latest_request_payment(db, req.id)
    latest_notes = _parse_notes_metadata(latest_payment.notes if latest_payment else None)
    requested_amount = int((latest_payment.amount or 0) if latest_payment else round(_request_total(req)))
    repair_code = _resolved_repair_code(req)

    return {
        "id": req.id,
        "client_id": req.client_id,
        "client_name": req.client.name if req.client else None,
        "repair_id": req.repair_id,
        "repair_number": req.repair.repair_number if req.repair else None,
        "repair_code": repair_code,
        "created_by": req.created_by,
        "status": req.status,
        "notes": req.notes,
        "created_at": req.created_at.isoformat() if req.created_at else None,
        "updated_at": req.updated_at.isoformat() if req.updated_at else None,
        "items_count": len(req.items or []),
        "total_items_amount": _request_total(req),
        "requested_amount": requested_amount,
        "payment_due_date": (
            latest_payment.payment_due_date.isoformat()
            if latest_payment and latest_payment.payment_due_date
            else None
        ),
        "latest_payment": (
            {
                "id": latest_payment.id,
                "status": latest_payment.status.value
                if isinstance(latest_payment.status, PaymentStatus)
                else str(latest_payment.status),
                "amount": latest_payment.amount,
                "payment_method": latest_payment.payment_method,
                "transaction_id": latest_payment.transaction_id,
                "payment_date": latest_payment.payment_date.isoformat()
                if latest_payment.payment_date
                else None,
                "payment_due_date": latest_payment.payment_due_date.isoformat()
                if latest_payment.payment_due_date
                else None,
                "proof_path": latest_notes.get("proof_path"),
                "deposit_reference": latest_notes.get("deposit_reference"),
                "depositor_name": latest_notes.get("depositor_name"),
                "client_notes": latest_notes.get("client_notes"),
                "admin_notes": latest_notes.get("admin_notes"),
            }
            if latest_payment
            else None
        ),
    }


def _checkout_external_id(payload: dict[str, Any] | None) -> str | None:
    raw = payload or {}
    for key in ("preference_id", "token", "id", "buy_order"):
        value = str(raw.get(key) or "").strip()
        if value:
            return value
    return None


def build_purchase_request_checkout_snapshot(
    req: PurchaseRequest,
    payment: Payment | None,
) -> dict[str, Any]:
    total_items_amount = _request_total(req)
    return {
        "request_id": req.id,
        "client_id": req.client_id,
        "repair_id": req.repair_id,
        "repair_code": _resolved_repair_code(req),
        "status": _normalize_status(req.status, fallback="draft"),
        "notes": req.notes,
        "total_items_amount": total_items_amount,
        "requested_amount": int((payment.amount or 0) if payment else round(total_items_amount)),
        "currency": str((payment.currency if payment else None) or "CLP"),
        "payment_due_date": (
            payment.payment_due_date.isoformat()
            if payment and payment.payment_due_date
            else None
        ),
        "items": _request_items_snapshot(req),
        "shipping": _request_shipping_snapshot(req),
    }


def attach_checkout_contract_to_payment(
    db: Session,
    payment: Payment,
    *,
    provider: str,
    origin_channel: str,
    return_url: str,
    notification_url: str | None,
    gateway_payload: dict[str, Any] | None,
) -> None:
    metadata = _parse_notes_metadata(payment.notes)
    checkout = metadata.get("checkout")
    if not isinstance(checkout, dict):
        checkout = {}

    checkout["version"] = (
        "purchase_request_checkout_v1"
        if payment.purchase_request_id
        else "payment_checkout_v1"
    )
    checkout["kind"] = "gateway_session"
    checkout["provider"] = str(provider or payment.payment_processor or payment.payment_method or "").strip()
    checkout["provider_status"] = "initiated"
    checkout["origin_channel"] = str(origin_channel or "").strip() or "admin_payment_gateway"
    checkout["gateway_reference"] = payment.transaction_id
    checkout["gateway_external_id"] = _checkout_external_id(gateway_payload)
    checkout["return_url"] = str(return_url or "").strip()
    checkout["notification_url"] = str(notification_url or "").strip() or None
    checkout["expires_at"] = payment.payment_due_date.isoformat() if payment.payment_due_date else None
    checkout["initiated_at"] = datetime.utcnow().isoformat()
    if gateway_payload:
        checkout["gateway_payload"] = gateway_payload

    if payment.purchase_request_id:
        req = _get_request_or_404(db, int(payment.purchase_request_id))
        checkout["request_snapshot"] = build_purchase_request_checkout_snapshot(req, payment)

    metadata["checkout"] = checkout
    payment.notes = json.dumps(metadata, ensure_ascii=False)


def update_checkout_status_metadata(
    payment: Payment,
    *,
    provider_status: str,
    provider_payload: dict[str, Any] | None,
    provider: str | None = None,
) -> None:
    metadata = _parse_notes_metadata(payment.notes)
    checkout = metadata.get("checkout")
    if not isinstance(checkout, dict):
        checkout = {}

    resolved_provider = str(
        provider
        or checkout.get("provider")
        or payment.payment_processor
        or payment.payment_method
        or ""
    ).strip()
    checkout["provider"] = resolved_provider or None
    checkout["provider_status"] = str(provider_status or "").strip() or "unknown"
    checkout["gateway_external_id"] = (
        _checkout_external_id(provider_payload) or checkout.get("gateway_external_id")
    )
    checkout["provider_payload"] = provider_payload or {}
    checkout["last_sync_at"] = datetime.utcnow().isoformat()
    if checkout["provider_status"] in {"approved", "success"}:
        checkout["paid_at"] = datetime.utcnow().isoformat()

    metadata["checkout"] = checkout
    payment.notes = json.dumps(metadata, ensure_ascii=False)


def sync_purchase_request_with_payment_result(
    db: Session,
    payment: Payment,
    *,
    source: str,
    provider: str | None = None,
    provider_status: str | None = None,
    user_id: int | None = None,
) -> dict[str, Any] | None:
    if not payment.purchase_request_id:
        return None

    req = _get_request_or_404(db, int(payment.purchase_request_id))
    previous_status = req.status
    normalized_status = _normalize_status(req.status, fallback="draft")
    resolved_provider = str(
        provider or payment.payment_processor or payment.payment_method or "gateway"
    ).strip() or "gateway"
    resolved_provider_status = str(provider_status or "").strip().lower() or "unknown"

    note_changed = False
    audit_event = None
    audit_message = None
    audit_details: dict[str, Any] = {
        "request_id": req.id,
        "payment_id": payment.id,
        "provider": resolved_provider,
        "provider_status": resolved_provider_status,
        "source": source,
    }

    if payment.status == PaymentStatus.SUCCESS:
        if normalized_status != "paid_client":
            req.status = "paid_client"
        updated_notes = _append_request_note(
            req.notes,
            f"Pago confirmado por {resolved_provider} ({resolved_provider_status})",
        )
        note_changed = updated_notes != str(req.notes or "")
        req.notes = updated_notes
        audit_event = "purchase_request.payment_confirmed"
        audit_message = f"Payment confirmed for purchase request #{req.id}"
        audit_details["result"] = "success"
    elif payment.status == PaymentStatus.FAILED:
        if normalized_status not in {"cancelled", "received", "applied_ot", "paid_client"}:
            req.status = "pending_payment"
        updated_notes = _append_request_note(
            req.notes,
            f"Intento de pago {resolved_provider} fallido ({resolved_provider_status})",
        )
        note_changed = updated_notes != str(req.notes or "")
        req.notes = updated_notes
        audit_event = "purchase_request.payment_failed"
        audit_message = f"Payment failed for purchase request #{req.id}"
        audit_details["result"] = "failed"
    else:
        if normalized_status == "requested":
            req.status = "pending_payment"

    if req.status != previous_status:
        _apply_request_stock_state(
            db,
            req,
            previous_status=previous_status,
            next_status=req.status,
            user_id=user_id,
        )

    db.commit()
    db.refresh(req)
    db.refresh(payment)

    if audit_event and (req.status != previous_status or note_changed):
        try:
            create_audit(
                event_type=audit_event,
                user_id=user_id,
                details=audit_details,
                message=audit_message,
            )
        except Exception:
            pass

    return {"ok": True, "request": _serialize_request(db, req), "payment": payment}


def _append_request_note(raw_notes: str | None, message: str) -> str:
    text = str(raw_notes or "").strip()
    suffix = str(message or "").strip()
    if not suffix:
        return text
    if not text:
        return suffix
    if suffix in text:
        return text
    return f"{text} | {suffix}"


def _get_request_or_404(db: Session, request_id: int) -> PurchaseRequest:
    req = db.query(PurchaseRequest).filter(PurchaseRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Purchase request not found")
    return req


def list_purchase_requests_query(db: Session):
    return db.query(PurchaseRequest).order_by(PurchaseRequest.updated_at.desc()).all()


def build_purchase_requests_board(
    db: Session,
    *,
    status: str | None = None,
    client_id: int | None = None,
    repair_id: int | None = None,
) -> dict[str, Any]:
    query = db.query(PurchaseRequest)
    if status:
        query = query.filter(PurchaseRequest.status == _normalize_status(status))
    if client_id:
        query = query.filter(PurchaseRequest.client_id == client_id)
    if repair_id:
        query = query.filter(PurchaseRequest.repair_id == repair_id)

    requests = query.order_by(PurchaseRequest.updated_at.desc()).all()
    payload = [_serialize_request(db, req) for req in requests]

    counts = {key: 0 for key in sorted(VALID_STATUSES)}
    for req in requests:
        normalized = _normalize_status(req.status)
        counts[normalized] = counts.get(normalized, 0) + 1

    return {
        "requests": payload,
        "counts": counts,
        "total": len(payload),
    }


def create_purchase_request_record(
    payload: PurchaseRequestCreate,
    db: Session,
    user: dict | None,
) -> PurchaseRequest:
    req = PurchaseRequest(
        client_id=payload.client_id,
        repair_id=payload.repair_id,
        created_by=int(user.get("user_id")) if user else None,
        status="draft",
        notes=payload.notes,
    )
    db.add(req)
    db.commit()
    db.refresh(req)

    for item in payload.items:
        db.add(
            PurchaseRequestItem(
                request_id=req.id,
                product_id=item.product_id,
                sku=item.sku,
                name=item.name,
                quantity=item.quantity,
                unit_price=item.unit_price or 0.0,
                external_url=item.external_url,
                status="suggested",
            )
        )
    db.commit()
    db.refresh(req)

    try:
        create_audit(
            event_type="purchase_request.created",
            user_id=int(user.get("user_id")) if user and user.get("user_id") else None,
            details={
                "request_id": req.id,
                "repair_id": req.repair_id,
                "items": len(req.items or []),
            },
            message=f"Purchase request #{req.id} created",
        )
    except Exception:
        pass

    return req


def get_purchase_request_detail_payload(db: Session, request_id: int) -> dict[str, Any]:
    return _serialize_request(db, _get_request_or_404(db, request_id))


def list_purchase_request_payments_for_request(db: Session, request_id: int):
    _get_request_or_404(db, request_id)
    return (
        db.query(Payment)
        .filter(Payment.purchase_request_id == request_id)
        .order_by(Payment.created_at.desc())
        .all()
    )


def request_client_payment_for_request(
    request_id: int,
    payload: dict[str, Any],
    db: Session,
    user: dict | None,
) -> dict[str, Any]:
    req = _get_request_or_404(db, request_id)
    previous_status = req.status
    requested_amount = payload.get("amount")
    default_amount = int(round(_request_total(req)))
    amount = int(round(float(requested_amount if requested_amount is not None else default_amount)))
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")

    due_days = int(payload.get("due_days") or 3)
    due_days = min(max(due_days, 1), 30)
    due_date = datetime.utcnow() + timedelta(days=due_days)

    req.status = "pending_payment"
    if payload.get("notes"):
        req.notes = str(payload.get("notes")).strip()

    open_payment = (
        db.query(Payment)
        .filter(
            Payment.purchase_request_id == req.id,
            Payment.status == PaymentStatus.PENDING,
        )
        .order_by(Payment.id.desc())
        .first()
    )

    meta = _parse_notes_metadata(open_payment.notes if open_payment else None)
    meta["instruction"] = str(
        payload.get("instruction") or "Depositar el monto solicitado y subir comprobante."
    )
    meta["admin_notes"] = str(payload.get("admin_notes") or "")

    if open_payment:
        open_payment.amount = amount
        open_payment.payment_due_date = due_date
        open_payment.notes = json.dumps(meta, ensure_ascii=False)
    else:
        open_payment = Payment(
            user_id=req.created_by,
            repair_id=req.repair_id,
            purchase_request_id=req.id,
            amount=amount,
            payment_method="transfer",
            transaction_id=f"REQ-{req.id}-{int(datetime.utcnow().timestamp())}",
            status=PaymentStatus.PENDING,
            notes=json.dumps(meta, ensure_ascii=False),
            payment_due_date=due_date,
            payment_processor="manual",
            currency="CLP",
        )
        db.add(open_payment)

    _apply_request_stock_state(
        db,
        req,
        previous_status=previous_status,
        next_status=req.status,
        user_id=int(user.get("user_id")) if user and user.get("user_id") else None,
    )
    db.commit()
    db.refresh(req)
    db.refresh(open_payment)

    try:
        create_audit(
            event_type="purchase_request.payment_requested",
            user_id=int(user.get("user_id")) if user and user.get("user_id") else None,
            details={"request_id": req.id, "payment_id": open_payment.id, "amount": amount},
            message=f"Payment requested for purchase request #{req.id}",
        )
    except Exception:
        pass

    return {"ok": True, "request": _serialize_request(db, req), "payment": open_payment}


def expire_overdue_purchase_requests(
    db: Session,
    *,
    now: datetime | None = None,
    user: dict | None = None,
    user_id: int | None = None,
) -> dict[str, Any]:
    current_time = now or datetime.utcnow()
    actor_id = user_id
    if actor_id is None and user and user.get("user_id"):
        actor_id = int(user.get("user_id"))

    candidates = (
        db.query(PurchaseRequest)
        .filter(PurchaseRequest.status == "pending_payment")
        .order_by(PurchaseRequest.updated_at.asc(), PurchaseRequest.id.asc())
        .all()
    )

    expired_request_ids: list[int] = []

    for req in candidates:
        payment = (
            db.query(Payment)
            .filter(
                Payment.purchase_request_id == req.id,
                Payment.status == PaymentStatus.PENDING,
            )
            .order_by(Payment.id.desc())
            .first()
        )
        if not payment or not payment.payment_due_date:
            continue
        if payment.payment_due_date >= current_time:
            continue

        previous_status = req.status
        req.status = "cancelled"
        req.notes = _append_request_note(
            req.notes,
            f"Reserva vencida: pago no recibido antes de {payment.payment_due_date.strftime('%Y-%m-%d %H:%M')}",
        )

        meta = _parse_notes_metadata(payment.notes)
        meta["expired_at"] = current_time.isoformat()
        meta["expiry_reason"] = "payment_due_date_exceeded"
        payment.status = PaymentStatus.FAILED
        payment.notes = json.dumps(meta, ensure_ascii=False)

        _apply_request_stock_state(
            db,
            req,
            previous_status=previous_status,
            next_status=req.status,
            user_id=actor_id,
        )
        expired_request_ids.append(int(req.id))

    if not expired_request_ids:
        return {"ok": True, "expired": 0, "request_ids": []}

    db.commit()

    for request_id in expired_request_ids:
        try:
            create_audit(
                event_type="purchase_request.expired",
                user_id=actor_id,
                details={"request_id": request_id},
                message=f"Purchase request #{request_id} expired by overdue payment",
            )
        except Exception:
            pass

    return {"ok": True, "expired": len(expired_request_ids), "request_ids": expired_request_ids}


def confirm_client_payment_for_request(
    request_id: int,
    payload: dict[str, Any],
    db: Session,
    user: dict | None,
) -> dict[str, Any]:
    req = _get_request_or_404(db, request_id)
    previous_status = req.status
    payment_id = payload.get("payment_id")

    query = db.query(Payment).filter(Payment.purchase_request_id == req.id)
    if payment_id:
        query = query.filter(Payment.id == int(payment_id))
    payment = query.order_by(Payment.id.desc()).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found for this purchase request")

    notes = _parse_notes_metadata(payment.notes)
    notes["admin_notes"] = str(payload.get("admin_notes") or notes.get("admin_notes") or "")
    notes["confirmed_by"] = int(user.get("user_id")) if user and user.get("user_id") else None
    notes["confirmed_at"] = datetime.utcnow().isoformat()

    payment.status = PaymentStatus.SUCCESS
    payment.payment_date = datetime.utcnow()
    payment.notes = json.dumps(notes, ensure_ascii=False)

    req.status = "paid_client"
    _apply_request_stock_state(
        db,
        req,
        previous_status=previous_status,
        next_status=req.status,
        user_id=int(user.get("user_id")) if user and user.get("user_id") else None,
    )
    db.commit()
    db.refresh(req)
    db.refresh(payment)

    try:
        create_audit(
            event_type="purchase_request.payment_confirmed",
            user_id=int(user.get("user_id")) if user and user.get("user_id") else None,
            details={"request_id": req.id, "payment_id": payment.id},
            message=f"Payment confirmed for purchase request #{req.id}",
        )
    except Exception:
        pass

    return {"ok": True, "request": _serialize_request(db, req), "payment": payment}


def update_purchase_request_status_record(
    request_id: int,
    *,
    status: str | None,
    payload: dict[str, Any] | None,
    db: Session,
    user: dict | None,
) -> dict[str, Any]:
    req = _get_request_or_404(db, request_id)
    previous_status = req.status
    incoming = payload or {}
    target_status = incoming.get("status") or status
    if not target_status:
        raise HTTPException(status_code=400, detail="status is required")

    req.status = _normalize_status(target_status, fallback=req.status or "draft")
    if "notes" in incoming:
        req.notes = str(incoming.get("notes") or "").strip() or None

    _apply_request_stock_state(
        db,
        req,
        previous_status=previous_status,
        next_status=req.status,
        user_id=int(user.get("user_id")) if user and user.get("user_id") else None,
    )
    db.commit()
    db.refresh(req)

    try:
        create_audit(
            event_type="purchase_request.status_updated",
            user_id=int(user.get("user_id")) if user and user.get("user_id") else None,
            details={"request_id": req.id, "status": req.status},
            message=f"Purchase request #{req.id} updated to {req.status}",
        )
    except Exception:
        pass

    return {"ok": True, "request": _serialize_request(db, req)}


def delete_purchase_request_record(
    request_id: int,
    db: Session,
    user: dict | None,
) -> None:
    req = _get_request_or_404(db, request_id)
    if _stock_phase(req.status) == "reserved":
        _release_request_reservations(
            db,
            req,
            user_id=int(user.get("user_id")) if user and user.get("user_id") else None,
        )

    db.query(Payment).filter(Payment.purchase_request_id == req.id).delete(
        synchronize_session=False
    )
    db.delete(req)
    db.commit()
