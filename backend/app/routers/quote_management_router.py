from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.client import Client
from app.models.quote import Quote, QuoteItem, QuoteRecipient, QuoteStatus
from app.models.repair import Repair
from app.services.email_service import EmailService
from app.services.event_system import Events, event_bus
from app.services.quote_management import (
    build_quote_board_response,
    build_quote_delivery_content,
    build_quote_item,
    build_quote_saved_event_payload,
    build_quote_recipient,
    can_transition_status,
    collect_quote_recipient_emails,
    default_quote_valid_until,
    ensure_default_recipient,
    generate_quote_number,
    get_quote_client,
    get_quote_or_404,
    mark_quote_as_sent,
    normalize_status,
    parse_iso_date,
    recalculate_quote_totals,
    rebalance_quote_recipients,
    replace_quote_items,
    replace_quote_recipients,
    resolve_quote_client,
    safe_create_quote_audit,
    send_quote_email_batch,
    serialize_quote,
    serialize_quote_with_client,
    to_float,
    update_quote_item_fields,
)
from app.services.whatsapp_service import WhatsAppService

router = APIRouter(tags=["quotes"])


def require_quote_permission(action: str):
    """
    Compatibilidad no destructiva:
    permite permisos nuevos (`quotes:*`) y legacy (`diagnostics:*`).
    """

    async def checker(
        user: dict = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> dict:
        from app.services.permission_service import PermissionService

        user_id = user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Usuario no identificado")
        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            raise HTTPException(status_code=401, detail="ID de usuario inválido")

        svc = PermissionService(db)
        if svc.has_permission(user_id, "quotes", action) or svc.has_permission(
            user_id, "diagnostics", action
        ):
            return user

        raise HTTPException(
            status_code=403,
            detail=f"No tiene permiso para {action} en quotes/diagnostics",
        )

    return checker

@router.get("")
async def list_quotes(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    client_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user: dict = Depends(require_quote_permission("read")),
):
    query = db.query(Quote)

    if status:
        normalized_status = str(status).strip().lower()
        if normalized_status not in QuoteStatus.ALL:
            raise HTTPException(status_code=400, detail="Invalid quote status")
        query = query.filter(Quote.status == normalized_status)
    if client_id:
        query = query.filter(Quote.client_id == client_id)

    quotes = query.order_by(Quote.created_at.desc()).offset(skip).limit(limit).all()
    client_ids = {quote.client_id for quote in quotes}
    clients = {}
    if client_ids:
        for client in db.query(Client).filter(Client.id.in_(client_ids)).all():
            clients[client.id] = client

    return [serialize_quote(quote, clients.get(quote.client_id)) for quote in quotes]


@router.get("/board")
async def quote_board(
    skip: int = 0,
    limit: int = 200,
    status: Optional[str] = None,
    client_id: Optional[int] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db),
    user: dict = Depends(require_quote_permission("read")),
):
    query = db.query(Quote)

    if status:
        normalized_status = str(status).strip().lower()
        if normalized_status not in QuoteStatus.ALL:
            raise HTTPException(status_code=400, detail="Invalid quote status")
        query = query.filter(Quote.status == normalized_status)

    if client_id:
        query = query.filter(Quote.client_id == client_id)

    text = str(q or "").strip()
    if text:
        like_query = f"%{text}%"
        query = (
            query.join(Client, Client.id == Quote.client_id)
            .filter(
                or_(
                    Quote.quote_number.ilike(like_query),
                    Quote.problem_description.ilike(like_query),
                    Quote.status.ilike(like_query),
                    Client.name.ilike(like_query),
                    Client.email.ilike(like_query),
                )
            )
        )

    quotes = query.order_by(Quote.created_at.desc()).offset(skip).limit(limit).all()
    client_ids = {quote.client_id for quote in quotes}
    clients = {}
    if client_ids:
        for client in db.query(Client).filter(Client.id.in_(client_ids)).all():
            clients[client.id] = client

    quote_ids = {quote.id for quote in quotes}
    linked_repairs = {}
    if quote_ids:
        for repair in db.query(Repair).filter(Repair.quote_id.in_(quote_ids)).all():
            if repair.quote_id and repair.quote_id not in linked_repairs:
                linked_repairs[repair.quote_id] = repair

    return build_quote_board_response(quotes, clients, linked_repairs)


@router.post("")
async def create_quote(
    quote_data: dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_quote_permission("create")),
):
    if not quote_data.get("problem_description"):
        raise HTTPException(status_code=400, detail="Campo requerido: problem_description")

    items_payload = quote_data.get("items") or []
    if not items_payload and quote_data.get("estimated_total") is None:
        raise HTTPException(
            status_code=400,
            detail="Campo requerido: estimated_total o items",
        )

    client = resolve_quote_client(db, quote_data)
    quote_number = generate_quote_number(db)
    user_id = int(user.get("user_id")) if user and user.get("user_id") else None

    new_quote = Quote(
        quote_number=quote_number,
        client_id=client.id,
        device_id=quote_data.get("device_id"),
        problem_description=quote_data["problem_description"],
        photos_received=quote_data.get("photos_received"),
        diagnosis=quote_data.get("diagnosis"),
        estimated_hours=to_float(quote_data.get("estimated_hours"), 0),
        estimated_parts_cost=to_float(quote_data.get("estimated_parts_cost"), 0),
        estimated_labor_cost=to_float(quote_data.get("estimated_labor_cost"), 0),
        estimated_total=to_float(quote_data.get("estimated_total"), 0),
        status=normalize_status(quote_data.get("status")),
        valid_until=parse_iso_date(quote_data.get("valid_until"))
        or default_quote_valid_until(),
        created_by=user_id,
    )

    db.add(new_quote)
    db.flush()

    if isinstance(items_payload, list) and items_payload:
        replace_quote_items(new_quote, items_payload)
        recalculate_quote_totals(new_quote)

    recipients_payload = quote_data.get("recipients") or []
    if isinstance(recipients_payload, list) and recipients_payload:
        replace_quote_recipients(new_quote, recipients_payload)
    ensure_default_recipient(new_quote, client)

    db.commit()
    db.refresh(new_quote)

    safe_create_quote_audit(
        event_type="quote.created",
        user=user,
        details={
            "quote_id": new_quote.id,
            "quote_number": quote_number,
            "client_id": client.id,
            "estimated_total": new_quote.estimated_total,
        },
        message=f"Quote {quote_number} created",
    )

    return serialize_quote(new_quote, client)


@router.get("/{quote_id}")
async def get_quote(
    quote_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_quote_permission("read")),
):
    quote = get_quote_or_404(db, quote_id)
    return serialize_quote_with_client(db, quote)


@router.put("/{quote_id}")
async def update_quote(
    quote_id: int,
    quote_data: dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_quote_permission("update")),
):
    quote = get_quote_or_404(db, quote_id)

    if "client_id" in quote_data and quote_data.get("client_id"):
        client = db.query(Client).filter(Client.id == quote_data.get("client_id")).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        quote.client_id = client.id

    if "problem_description" in quote_data:
        quote.problem_description = (
            quote_data.get("problem_description") or quote.problem_description
        )
    if "photos_received" in quote_data:
        quote.photos_received = quote_data.get("photos_received")
    if "diagnosis" in quote_data:
        quote.diagnosis = quote_data.get("diagnosis")
    if "estimated_hours" in quote_data:
        quote.estimated_hours = to_float(
            quote_data.get("estimated_hours"), quote.estimated_hours or 0
        )
    if "valid_until" in quote_data:
        quote.valid_until = parse_iso_date(quote_data.get("valid_until"))
    if "client_response" in quote_data:
        quote.client_response = quote_data.get("client_response")
    if "responded_at" in quote_data:
        parsed_responded = parse_iso_date(quote_data.get("responded_at"))
        quote.responded_at = (
            datetime.combine(parsed_responded, datetime.min.time())
            if parsed_responded
            else None
        )

    status_changed = False
    if "status" in quote_data:
        raw_status = str(quote_data.get("status") or "").strip().lower()
        if raw_status not in QuoteStatus.ALL:
            raise HTTPException(status_code=400, detail="Invalid quote status")
        target_status = raw_status
        if not can_transition_status(quote.status, target_status):
            raise HTTPException(
                status_code=400,
                detail=f"Transición de estado no permitida: {quote.status} -> {target_status}",
            )
        status_changed = target_status != quote.status
        quote.status = target_status
        if target_status in (QuoteStatus.APPROVED, QuoteStatus.DENIED) and not quote.responded_at:
            quote.responded_at = datetime.utcnow()

    items_replaced = False
    if "items" in quote_data and isinstance(quote_data.get("items"), list):
        replace_quote_items(quote, quote_data.get("items"))
        recalculate_quote_totals(quote)
        items_replaced = True

    if "recipients" in quote_data and isinstance(quote_data.get("recipients"), list):
        replace_quote_recipients(quote, quote_data.get("recipients"))

    client = get_quote_client(db, quote)
    ensure_default_recipient(quote, client)

    if not items_replaced:
        if "estimated_parts_cost" in quote_data:
            quote.estimated_parts_cost = to_float(
                quote_data.get("estimated_parts_cost"), quote.estimated_parts_cost
            )
        if "estimated_labor_cost" in quote_data:
            quote.estimated_labor_cost = to_float(
                quote_data.get("estimated_labor_cost"), quote.estimated_labor_cost
            )
        if "estimated_total" in quote_data:
            quote.estimated_total = to_float(
                quote_data.get("estimated_total"), quote.estimated_total
            )

    db.commit()
    db.refresh(quote)

    safe_create_quote_audit(
        event_type="quote.updated",
        user=user,
        details={
            "quote_id": quote.id,
            "quote_number": quote.quote_number,
            "status_changed": status_changed,
        },
        message=f"Quote {quote.quote_number} updated",
    )

    return serialize_quote_with_client(db, quote)


@router.delete("/{quote_id}")
async def delete_quote(
    quote_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_quote_permission("update")),
):
    quote = get_quote_or_404(db, quote_id)
    linked_repairs = db.query(Repair).filter(Repair.quote_id == quote.id).count()
    if linked_repairs:
        raise HTTPException(
            status_code=400, detail="No se puede eliminar una cotización asociada a una OT"
        )

    db.delete(quote)
    db.commit()
    return {"ok": True}


@router.post("/{quote_id}/status")
async def update_quote_status(
    quote_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_quote_permission("approve")),
):
    quote = get_quote_or_404(db, quote_id)
    raw_status = str(payload.get("status") or "").strip().lower()
    if raw_status not in QuoteStatus.ALL:
        raise HTTPException(status_code=400, detail="Invalid quote status")
    target_status = raw_status

    if not can_transition_status(quote.status, target_status):
        raise HTTPException(
            status_code=400,
            detail=f"Transición de estado no permitida: {quote.status} -> {target_status}",
        )

    quote.status = target_status
    if payload.get("client_response") is not None:
        quote.client_response = payload.get("client_response")
    if target_status in (QuoteStatus.APPROVED, QuoteStatus.DENIED):
        quote.responded_at = datetime.utcnow()

    db.commit()
    db.refresh(quote)
    client = get_quote_client(db, quote)

    safe_create_quote_audit(
        event_type="quote.status_changed",
        user=user,
        details={
            "quote_id": quote.id,
            "quote_number": quote.quote_number,
            "status": quote.status,
        },
        message=f"Quote {quote.quote_number} status changed to {quote.status}",
    )

    return serialize_quote_with_client(db, quote)


@router.post("/{quote_id}/send")
async def send_quote(
    quote_id: int,
    payload: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: dict = Depends(require_quote_permission("update")),
):
    quote = get_quote_or_404(db, quote_id)
    client = db.query(Client).filter(Client.id == quote.client_id).first()
    ensure_default_recipient(quote, client)

    recipient_emails = collect_quote_recipient_emails(quote)
    if not recipient_emails:
        raise HTTPException(status_code=400, detail="Quote has no recipients")

    custom_message = str(payload.get("message") or "").strip()
    delivery_content = build_quote_delivery_content(quote, client, custom_message)

    email_service = EmailService()
    sent_to, failed_to = send_quote_email_batch(
        email_service,
        recipient_emails,
        delivery_content["subject"],
        delivery_content["html_content"],
    )

    whatsapp_queued = False
    if payload.get("send_whatsapp", False) and client and client.phone:
        background_tasks.add_task(
            WhatsAppService().send_text,
            to_phone=client.phone,
            message=(
                f"Cotización {quote.quote_number}: total estimado ${quote.estimated_total or 0:,.0f} CLP. "
                f"Revisa tu correo para el detalle."
            ),
        )
        whatsapp_queued = True

    mark_quote_as_sent(quote)

    db.commit()
    db.refresh(quote)

    safe_create_quote_audit(
        event_type="quote.sent",
        user=user,
        details={
            "quote_id": quote.id,
            "quote_number": quote.quote_number,
            "sent_to": sent_to,
            "failed_to": failed_to,
            "whatsapp_queued": whatsapp_queued,
        },
        message=f"Quote {quote.quote_number} sent",
    )

    try:
        event_bus.emit(
            Events.QUOTATION_SAVED,
            build_quote_saved_event_payload(quote, client, sent_to),
        )
    except Exception:
        pass

    return {
        "quote": serialize_quote(quote, client),
        "sent_to": sent_to,
        "failed_to": failed_to,
        "whatsapp_queued": whatsapp_queued,
    }


@router.post("/{quote_id}/items")
async def add_quote_item(
    quote_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_quote_permission("update")),
):
    quote = get_quote_or_404(db, quote_id)
    sort_order = len(quote.items)
    quote.items.append(build_quote_item(payload, sort_order=sort_order))
    recalculate_quote_totals(quote)

    db.commit()
    db.refresh(quote)
    return serialize_quote_with_client(db, quote)


@router.put("/{quote_id}/items/{item_id}")
async def update_quote_item(
    quote_id: int,
    item_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_quote_permission("update")),
):
    quote = get_quote_or_404(db, quote_id)
    item = (
        db.query(QuoteItem)
        .filter(QuoteItem.id == item_id, QuoteItem.quote_id == quote.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Quote item not found")

    update_quote_item_fields(item, payload)
    recalculate_quote_totals(quote)
    db.commit()
    db.refresh(quote)
    return serialize_quote_with_client(db, quote)


@router.delete("/{quote_id}/items/{item_id}")
async def delete_quote_item(
    quote_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_quote_permission("update")),
):
    quote = get_quote_or_404(db, quote_id)
    item = (
        db.query(QuoteItem)
        .filter(QuoteItem.id == item_id, QuoteItem.quote_id == quote.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Quote item not found")

    db.delete(item)
    db.flush()
    recalculate_quote_totals(quote)
    db.commit()
    db.refresh(quote)
    return serialize_quote_with_client(db, quote)


@router.post("/{quote_id}/recipients")
async def add_quote_recipient(
    quote_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_quote_permission("update")),
):
    quote = get_quote_or_404(db, quote_id)
    recipient = build_quote_recipient(payload, index=len(quote.recipients))
    if not recipient.email:
        raise HTTPException(status_code=400, detail="Campo requerido: email")

    if recipient.is_primary:
        for existing in quote.recipients:
            existing.is_primary = False

    quote.recipients.append(recipient)
    db.commit()
    db.refresh(quote)
    return serialize_quote_with_client(db, quote)


@router.delete("/{quote_id}/recipients/{recipient_id}")
async def delete_quote_recipient(
    quote_id: int,
    recipient_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_quote_permission("update")),
):
    quote = get_quote_or_404(db, quote_id)
    recipient = (
        db.query(QuoteRecipient)
        .filter(QuoteRecipient.id == recipient_id, QuoteRecipient.quote_id == quote.id)
        .first()
    )
    if not recipient:
        raise HTTPException(status_code=404, detail="Quote recipient not found")

    db.delete(recipient)
    db.flush()
    client = get_quote_client(db, quote)
    rebalance_quote_recipients(quote, client)

    db.commit()
    db.refresh(quote)
    return serialize_quote_with_client(db, quote)


def build_router(*, deprecated: bool = False) -> APIRouter:
    fresh_router = APIRouter(tags=["quotes"])
    fresh_router.add_api_route("", list_quotes, methods=["GET"], deprecated=deprecated)
    fresh_router.add_api_route("/board", quote_board, methods=["GET"], deprecated=deprecated)
    fresh_router.add_api_route("", create_quote, methods=["POST"], deprecated=deprecated)
    fresh_router.add_api_route("/{quote_id}", get_quote, methods=["GET"], deprecated=deprecated)
    fresh_router.add_api_route("/{quote_id}", update_quote, methods=["PUT"], deprecated=deprecated)
    fresh_router.add_api_route("/{quote_id}", delete_quote, methods=["DELETE"], deprecated=deprecated)
    fresh_router.add_api_route(
        "/{quote_id}/status",
        update_quote_status,
        methods=["POST"],
        deprecated=deprecated,
    )
    fresh_router.add_api_route(
        "/{quote_id}/send",
        send_quote,
        methods=["POST"],
        deprecated=deprecated,
    )
    fresh_router.add_api_route(
        "/{quote_id}/items",
        add_quote_item,
        methods=["POST"],
        deprecated=deprecated,
    )
    fresh_router.add_api_route(
        "/{quote_id}/items/{item_id}",
        update_quote_item,
        methods=["PUT"],
        deprecated=deprecated,
    )
    fresh_router.add_api_route(
        "/{quote_id}/items/{item_id}",
        delete_quote_item,
        methods=["DELETE"],
        deprecated=deprecated,
    )
    fresh_router.add_api_route(
        "/{quote_id}/recipients",
        add_quote_recipient,
        methods=["POST"],
        deprecated=deprecated,
    )
    fresh_router.add_api_route(
        "/{quote_id}/recipients/{recipient_id}",
        delete_quote_recipient,
        methods=["DELETE"],
        deprecated=deprecated,
    )
    return fresh_router
