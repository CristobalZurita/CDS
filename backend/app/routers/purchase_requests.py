import json
from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_permission, get_current_user
from app.models.inventory import Product
from app.models.payment import Payment, PaymentStatus
from app.models.purchase_request import PurchaseRequest, PurchaseRequestItem
from app.models.stock import Stock
from app.models.stock_movement import StockMovement
from app.schemas import PaymentRead
from app.schemas.purchase_request import PurchaseRequestCreate, PurchaseRequestOut
from app.services.logging_service import create_audit
from app.services.ot_code_service import repair_code as _repair_code

router = APIRouter(prefix="/purchase-requests", tags=["purchase_requests"])

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
    repair = req.repair
    if not repair:
        return None

    if repair.repair_number and not str(repair.repair_number).startswith("R-"):
        return repair.repair_number

    client_id = int(req.client_id or 0) or None
    if not client_id:
        return repair.repair_number

    if repair.ot_parent_id and repair.ot_sequence:
        if repair.ot_parent_id == repair.id:
            if int(repair.ot_sequence) <= 1:
                return _repair_code(client_id, repair.id)
            return _repair_code(client_id, repair.id, int(repair.ot_sequence))
        return _repair_code(client_id, int(repair.ot_parent_id), int(repair.ot_sequence))

    return _repair_code(client_id, repair.id)


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
                "status": latest_payment.status.value if isinstance(latest_payment.status, PaymentStatus) else str(latest_payment.status),
                "amount": latest_payment.amount,
                "payment_method": latest_payment.payment_method,
                "transaction_id": latest_payment.transaction_id,
                "payment_date": latest_payment.payment_date.isoformat() if latest_payment.payment_date else None,
                "payment_due_date": latest_payment.payment_due_date.isoformat() if latest_payment.payment_due_date else None,
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


def _get_request_or_404(db: Session, request_id: int) -> PurchaseRequest:
    req = db.query(PurchaseRequest).filter(PurchaseRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Purchase request not found")
    return req


@router.get("/", response_model=List[PurchaseRequestOut])
def list_purchase_requests(
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("purchase_requests", "read")),
):
    requests = db.query(PurchaseRequest).order_by(PurchaseRequest.updated_at.desc()).all()
    return requests


@router.get("/board")
def list_purchase_requests_board(
    status: str | None = Query(default=None),
    client_id: int | None = Query(default=None),
    repair_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("purchase_requests", "read")),
):
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


@router.post("/", response_model=PurchaseRequestOut, status_code=201)
def create_purchase_request(
    payload: PurchaseRequestCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
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
        req_item = PurchaseRequestItem(
            request_id=req.id,
            product_id=item.product_id,
            sku=item.sku,
            name=item.name,
            quantity=item.quantity,
            unit_price=item.unit_price or 0.0,
            external_url=item.external_url,
            status="suggested",
        )
        db.add(req_item)
    db.commit()
    db.refresh(req)

    try:
        create_audit(
            event_type="purchase_request.created",
            user_id=int(user.get("user_id")) if user and user.get("user_id") else None,
            details={"request_id": req.id, "repair_id": req.repair_id, "items": len(req.items or [])},
            message=f"Purchase request #{req.id} created",
        )
    except Exception:
        pass

    return req


@router.get("/{request_id}", response_model=PurchaseRequestOut)
def get_purchase_request(
    request_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("purchase_requests", "read")),
):
    return _get_request_or_404(db, request_id)


@router.get("/{request_id}/detail")
def get_purchase_request_detail(
    request_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("purchase_requests", "read")),
):
    req = _get_request_or_404(db, request_id)
    return _serialize_request(db, req)


@router.get("/{request_id}/payments", response_model=List[PaymentRead])
def list_purchase_request_payments(
    request_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("purchase_requests", "read")),
):
    _get_request_or_404(db, request_id)
    return (
        db.query(Payment)
        .filter(Payment.purchase_request_id == request_id)
        .order_by(Payment.created_at.desc())
        .all()
    )


@router.post("/{request_id}/request-payment")
def request_client_payment(
    request_id: int,
    payload: dict = Body(default={}),
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("purchase_requests", "update")),
):
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
        .filter(Payment.purchase_request_id == req.id, Payment.status == PaymentStatus.PENDING)
        .order_by(Payment.id.desc())
        .first()
    )

    meta = _parse_notes_metadata(open_payment.notes if open_payment else None)
    meta["instruction"] = str(payload.get("instruction") or "Depositar el monto solicitado y subir comprobante.")
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


@router.post("/{request_id}/confirm-payment")
def confirm_client_payment(
    request_id: int,
    payload: dict = Body(default={}),
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("purchase_requests", "update")),
):
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


@router.patch("/{request_id}")
def update_purchase_request_status(
    request_id: int,
    status: str | None = Query(default=None),
    payload: dict | None = Body(default=None),
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("purchase_requests", "update")),
):
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


@router.delete("/{request_id}", status_code=204)
def delete_purchase_request(
    request_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("purchase_requests", "delete")),
):
    req = _get_request_or_404(db, request_id)
    if _stock_phase(req.status) == "reserved":
        _release_request_reservations(
            db,
            req,
            user_id=int(user.get("user_id")) if user and user.get("user_id") else None,
        )

    db.query(Payment).filter(Payment.purchase_request_id == req.id).delete(synchronize_session=False)
    db.delete(req)
    db.commit()
    return None
