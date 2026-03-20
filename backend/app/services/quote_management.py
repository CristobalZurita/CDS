"""Quote domain helpers (aditivo, sin romper endpoints existentes)."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from fastapi import BackgroundTasks, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.business_config import business_config
from app.models.client import Client
from app.models.quote import Quote, QuoteItem, QuoteRecipient, QuoteStatus
from app.models.repair import Repair
from app.services.email_service import EmailService, build_email_html
from app.services.event_system import Events, event_bus
from app.services.logging_service import create_audit
from app.services.whatsapp_service import WhatsAppService

_PART_ITEM_TYPES = {"part", "repuesto", "material", "component"}
_LABOR_ITEM_TYPES = {"labor", "service", "mano_obra", "diagnostic"}
_STATUS_TRANSITIONS = {
    QuoteStatus.PENDING: {QuoteStatus.SENT, QuoteStatus.CANCELED},
    QuoteStatus.SENT: {QuoteStatus.APPROVED, QuoteStatus.DENIED, QuoteStatus.CANCELED},
    QuoteStatus.APPROVED: {QuoteStatus.CANCELED},
    QuoteStatus.DENIED: {QuoteStatus.CANCELED},
    QuoteStatus.CANCELED: set(),
}


def to_float(value: Any, default: float = 0.0) -> float:
    if value in (None, ""):
        return float(default)
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def parse_iso_date(value: Any) -> date | None:
    if not value:
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            return datetime.fromisoformat(text).date()
        except ValueError:
            return None
    return None


def normalize_status(value: str | None) -> str:
    if not value:
        return QuoteStatus.PENDING
    normalized = str(value).strip().lower()
    return normalized if normalized in QuoteStatus.ALL else QuoteStatus.PENDING


def default_quote_valid_until() -> date:
    return datetime.utcnow().date() + timedelta(days=30)


def generate_quote_number(db: Session) -> str:
    year = datetime.utcnow().strftime("%Y")
    last_quote = (
        db.query(Quote)
        .filter(Quote.quote_number.like(f"COT-{year}-%"))
        .order_by(Quote.id.desc())
        .first()
    )

    if last_quote:
        try:
            last_num = int(last_quote.quote_number.split("-")[-1])
            next_num = last_num + 1
        except (ValueError, IndexError):
            next_num = 1
    else:
        next_num = 1

    return f"COT-{year}-{next_num:04d}"


def get_quote_or_404(db: Session, quote_id: int) -> Quote:
    quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    return quote


def resolve_quote_client(db: Session, payload: dict[str, Any]) -> Client:
    client_id = payload.get("client_id")
    if client_id:
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        return client

    client_email = str(payload.get("client_email") or "").strip().lower()
    client_name = str(payload.get("client_name") or "").strip()

    if not client_email:
        raise HTTPException(
            status_code=400, detail="Campo requerido: client_email o client_id"
        )
    if not client_name:
        raise HTTPException(status_code=400, detail="Campo requerido: client_name")

    client = db.query(Client).filter(Client.email == client_email).first()
    if client:
        if not client.name and client_name:
            client.name = client_name
        if payload.get("client_phone") and not client.phone:
            client.phone = payload.get("client_phone")
        return client

    client = Client(
        name=client_name,
        email=client_email,
        phone=payload.get("client_phone"),
    )
    db.add(client)
    db.flush()
    return client


def assign_quote_client(db: Session, quote: Quote, client_id: Any) -> Client:
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    quote.client_id = client.id
    return client


def fetch_quote_client_map(db: Session, quotes: list[Quote]) -> dict[int, Client]:
    client_ids = {quote.client_id for quote in quotes if quote.client_id}
    if not client_ids:
        return {}
    return {
        client.id: client
        for client in db.query(Client).filter(Client.id.in_(client_ids)).all()
    }


def fetch_linked_repairs_by_quote_id(db: Session, quotes: list[Quote]) -> dict[int, Repair]:
    quote_ids = {quote.id for quote in quotes if quote.id}
    if not quote_ids:
        return {}

    linked_repairs: dict[int, Repair] = {}
    for repair in db.query(Repair).filter(Repair.quote_id.in_(quote_ids)).all():
        if repair.quote_id and repair.quote_id not in linked_repairs:
            linked_repairs[repair.quote_id] = repair
    return linked_repairs


def build_quote_query(query, *, status: Any = None, client_id: Any = None):
    if status:
        normalized_status = str(status).strip().lower()
        if normalized_status not in QuoteStatus.ALL:
            raise HTTPException(status_code=400, detail="Invalid quote status")
        query = query.filter(Quote.status == normalized_status)

    if client_id:
        query = query.filter(Quote.client_id == client_id)

    return query


def apply_quote_search(query, text: Any):
    value = str(text or "").strip()
    if not value:
        return query

    like_query = f"%{value}%"
    return (
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


def can_transition_status(current: str | None, new_status: str | None) -> bool:
    source = normalize_status(current)
    target = normalize_status(new_status)
    if source == target:
        return True
    return target in _STATUS_TRANSITIONS.get(source, set())


def validate_quote_creation_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    if not payload.get("problem_description"):
        raise HTTPException(status_code=400, detail="Campo requerido: problem_description")

    items_payload = payload.get("items") or []
    if not items_payload and payload.get("estimated_total") is None:
        raise HTTPException(
            status_code=400,
            detail="Campo requerido: estimated_total o items",
        )
    return items_payload


def build_quote_model(
    payload: dict[str, Any],
    *,
    quote_number: str,
    client_id: int,
    created_by: int | None,
) -> Quote:
    return Quote(
        quote_number=quote_number,
        client_id=client_id,
        device_id=payload.get("device_id"),
        problem_description=payload["problem_description"],
        photos_received=payload.get("photos_received"),
        diagnosis=payload.get("diagnosis"),
        estimated_hours=to_float(payload.get("estimated_hours"), 0),
        estimated_parts_cost=to_float(payload.get("estimated_parts_cost"), 0),
        estimated_labor_cost=to_float(payload.get("estimated_labor_cost"), 0),
        estimated_total=to_float(payload.get("estimated_total"), 0),
        status=normalize_status(payload.get("status")),
        valid_until=parse_iso_date(payload.get("valid_until")) or default_quote_valid_until(),
        created_by=created_by,
    )


def apply_quote_payload_updates(quote: Quote, payload: dict[str, Any]) -> None:
    if "problem_description" in payload:
        quote.problem_description = payload.get("problem_description") or quote.problem_description
    if "photos_received" in payload:
        quote.photos_received = payload.get("photos_received")
    if "diagnosis" in payload:
        quote.diagnosis = payload.get("diagnosis")
    if "estimated_hours" in payload:
        quote.estimated_hours = to_float(payload.get("estimated_hours"), quote.estimated_hours or 0)
    if "valid_until" in payload:
        quote.valid_until = parse_iso_date(payload.get("valid_until"))
    if "client_response" in payload:
        quote.client_response = payload.get("client_response")
    if "responded_at" in payload:
        parsed_responded = parse_iso_date(payload.get("responded_at"))
        quote.responded_at = (
            datetime.combine(parsed_responded, datetime.min.time())
            if parsed_responded
            else None
        )


def apply_quote_status_transition(
    quote: Quote,
    status: Any,
    *,
    client_response: Any | None = None,
) -> bool:
    raw_status = str(status or "").strip().lower()
    if raw_status not in QuoteStatus.ALL:
        raise HTTPException(status_code=400, detail="Invalid quote status")
    if not can_transition_status(quote.status, raw_status):
        raise HTTPException(
            status_code=400,
            detail=f"Transición de estado no permitida: {quote.status} -> {raw_status}",
        )

    status_changed = raw_status != quote.status
    quote.status = raw_status
    if client_response is not None:
        quote.client_response = client_response
    if raw_status in (QuoteStatus.APPROVED, QuoteStatus.DENIED) and not quote.responded_at:
        quote.responded_at = datetime.utcnow()
    return status_changed


def build_quote_item(payload: dict[str, Any], sort_order: int = 0) -> QuoteItem:
    quantity = to_float(payload.get("quantity"), 1.0)
    unit_price = to_float(payload.get("unit_price"), 0.0)
    line_total = payload.get("line_total")

    item = QuoteItem(
        item_type=str(payload.get("item_type") or "service").strip().lower(),
        sku=(payload.get("sku") or None),
        name=str(payload.get("name") or "").strip() or "ITEM",
        description=(payload.get("description") or None),
        quantity=quantity,
        unit_price=unit_price,
        line_total=to_float(line_total, quantity * unit_price),
        sort_order=sort_order,
        source_table=(payload.get("source_table") or None),
        source_id=payload.get("source_id"),
    )

    if line_total in (None, ""):
        item.recalculate_line_total()

    return item


def build_quote_recipient(payload: dict[str, Any], index: int = 0) -> QuoteRecipient:
    return QuoteRecipient(
        name=(payload.get("name") or None),
        email=str(payload.get("email") or "").strip().lower(),
        is_primary=bool(payload.get("is_primary")) or index == 0,
    )


def replace_quote_items(quote: Quote, payload_items: list[dict[str, Any]]) -> None:
    quote.items.clear()
    for idx, payload in enumerate(payload_items):
        quote.items.append(build_quote_item(payload, sort_order=idx))


def replace_quote_recipients(quote: Quote, payload_recipients: list[dict[str, Any]]) -> None:
    quote.recipients.clear()
    for idx, payload in enumerate(payload_recipients):
        recipient = build_quote_recipient(payload, index=idx)
        if recipient.email:
            quote.recipients.append(recipient)


def ensure_default_recipient(quote: Quote, client: Client | None) -> None:
    if quote.recipients:
        return
    if client and client.email:
        quote.recipients.append(
            QuoteRecipient(
                name=client.name,
                email=client.email.strip().lower(),
                is_primary=True,
            )
        )


def quote_bucket(status: str | None) -> str:
    current = normalize_status(status)
    if current == QuoteStatus.PENDING:
        return "draft_pending"
    if current == QuoteStatus.SENT:
        return "waiting_response"
    return "closed"


def recalculate_quote_totals(quote: Quote) -> None:
    parts_total = 0.0
    labor_total = 0.0
    grand_total = 0.0

    for item in quote.items or []:
        if item.line_total in (None, ""):
            item.recalculate_line_total()

        line_total = to_float(item.line_total)
        item_type = str(item.item_type or "service").strip().lower()
        grand_total += line_total

        if item_type in _PART_ITEM_TYPES:
            parts_total += line_total
        elif item_type in _LABOR_ITEM_TYPES:
            labor_total += line_total

    quote.estimated_parts_cost = round(parts_total, 2)
    quote.estimated_labor_cost = round(labor_total, 2)
    quote.estimated_total = round(max(grand_total, 0.0), 2)


def build_quote_board_response(
    quotes: list[Quote],
    clients_by_id: dict[int, Client],
    linked_repairs_by_quote_id: dict[int, Any],
) -> dict[str, Any]:
    board = {
        "draft_pending": [],
        "waiting_response": [],
        "closed": [],
    }
    status_counts = {
        QuoteStatus.PENDING: 0,
        QuoteStatus.SENT: 0,
        QuoteStatus.APPROVED: 0,
        QuoteStatus.DENIED: 0,
        QuoteStatus.CANCELED: 0,
    }
    expired_open = 0
    expiring_3d = 0
    today = datetime.utcnow().date()

    for quote in quotes:
        bucket = quote_bucket(quote.status)
        serialized = serialize_quote(quote, clients_by_id.get(quote.client_id))
        linked_repair = linked_repairs_by_quote_id.get(quote.id)
        if linked_repair:
            serialized["linked_repair_id"] = linked_repair.id
            serialized["linked_repair_number"] = linked_repair.repair_number
        else:
            serialized["linked_repair_id"] = None
            serialized["linked_repair_number"] = None
        board[bucket].append(serialized)

        normalized = normalize_status(quote.status)
        if normalized in status_counts:
            status_counts[normalized] += 1

        if quote.valid_until and normalized in (QuoteStatus.PENDING, QuoteStatus.SENT):
            if quote.valid_until < today:
                expired_open += 1
            elif quote.valid_until <= (today + timedelta(days=3)):
                expiring_3d += 1

    return {
        "counts": {
            "draft_pending": len(board["draft_pending"]),
            "waiting_response": len(board["waiting_response"]),
            "closed": len(board["closed"]),
            "total": len(quotes),
        },
        "metrics": {
            "pending": status_counts[QuoteStatus.PENDING],
            "sent": status_counts[QuoteStatus.SENT],
            "approved": status_counts[QuoteStatus.APPROVED],
            "denied": status_counts[QuoteStatus.DENIED],
            "canceled": status_counts[QuoteStatus.CANCELED],
            "expired_open": expired_open,
            "expiring_3d": expiring_3d,
            "open_total": status_counts[QuoteStatus.PENDING]
            + status_counts[QuoteStatus.SENT],
        },
        "board": board,
    }


def serialize_quotes_with_clients(db: Session, quotes: list[Quote]) -> list[dict[str, Any]]:
    clients = fetch_quote_client_map(db, quotes)
    return [serialize_quote(quote, clients.get(quote.client_id)) for quote in quotes]


def build_quote_board_snapshot(db: Session, quotes: list[Quote]) -> dict[str, Any]:
    return build_quote_board_response(
        quotes,
        fetch_quote_client_map(db, quotes),
        fetch_linked_repairs_by_quote_id(db, quotes),
    )


def _commit_quote(db: Session, quote: Quote) -> Quote:
    db.commit()
    db.refresh(quote)
    return quote


def _apply_quote_relations(
    quote: Quote,
    payload: dict[str, Any],
    *,
    client: Client | None,
    apply_estimate_overrides_when_no_items: bool,
) -> bool:
    items_replaced = False
    if "items" in payload and isinstance(payload.get("items"), list):
        replace_quote_items(quote, payload.get("items"))
        recalculate_quote_totals(quote)
        items_replaced = True

    if "recipients" in payload and isinstance(payload.get("recipients"), list):
        replace_quote_recipients(quote, payload.get("recipients"))

    ensure_default_recipient(quote, client)

    if apply_estimate_overrides_when_no_items and not items_replaced:
        apply_quote_estimate_overrides(quote, payload)

    return items_replaced


def collect_quote_recipient_emails(quote: Quote) -> list[str]:
    recipient_emails: list[str] = []
    for recipient in quote.recipients:
        email = str(recipient.email or "").strip().lower()
        if email and email not in recipient_emails:
            recipient_emails.append(email)
    return recipient_emails


def build_quote_delivery_content(
    quote: Quote,
    client: Client | None,
    custom_message: str = "",
) -> dict[str, str]:
    subject = business_config.quote_delivery_subject(quote.quote_number)
    item_rows = "".join(
        f"<tr><td>{item.name}</td><td>{item.quantity}</td><td>${item.unit_price:,.0f}</td><td>${item.line_total:,.0f}</td></tr>"
        for item in (quote.items or [])
    )
    if not item_rows:
        item_rows = "<tr><td colspan='4'>Sin ítems detallados</td></tr>"

    html_content = build_email_html(
        f"""
        <h2>Cotización {quote.quote_number}</h2>
        <p><strong>Cliente:</strong> {client.name if client else 'SIN_DATO'}</p>
        <p><strong>Problema reportado:</strong> {quote.problem_description}</p>
        <p><strong>Diagnóstico:</strong> {quote.diagnosis or 'SIN_DATO'}</p>
        <p><strong>Total estimado:</strong> ${quote.estimated_total or 0:,.0f} CLP</p>
        <p><strong>Válida hasta:</strong> {quote.valid_until.isoformat() if quote.valid_until else 'SIN_DATO'}</p>
        {f"<p>{custom_message}</p>" if custom_message else ""}
        <table class="email-table">
            <thead>
                <tr><th>Ítem</th><th>Cantidad</th><th>Unitario</th><th>Total</th></tr>
            </thead>
            <tbody>{item_rows}</tbody>
        </table>
        """,
    )

    return {
        "subject": subject,
        "html_content": html_content,
    }


def send_quote_email_batch(
    email_service: EmailService,
    recipient_emails: list[str],
    subject: str,
    html_content: str,
) -> tuple[list[str], list[str]]:
    sent_to: list[str] = []
    failed_to: list[str] = []

    for email in recipient_emails:
        ok = email_service.send_email(
            to_email=email,
            subject=subject,
            html_content=html_content,
        )
        if ok:
            sent_to.append(email)
        else:
            failed_to.append(email)

    return sent_to, failed_to


def mark_quote_as_sent(quote: Quote) -> None:
    if quote.status == QuoteStatus.PENDING:
        quote.status = QuoteStatus.SENT


def build_quote_saved_event_payload(
    quote: Quote,
    client: Client | None,
    sent_to: list[str],
) -> dict[str, Any]:
    return {
        "customer_email": sent_to[0] if sent_to else (client.email if client else None),
        "customer_name": client.name if client else "Cliente",
        "quotation_id": quote.quote_number,
        "instrument": business_config.quote_default_item_name,
        "min_price": quote.estimated_total or 0,
        "max_price": quote.estimated_total or 0,
    }


def extract_quote_actor_id(user: dict[str, Any] | None) -> int | None:
    if not user or not user.get("user_id"):
        return None
    try:
        return int(user.get("user_id"))
    except (TypeError, ValueError):
        return None


def safe_create_quote_audit(
    *,
    event_type: str,
    user: dict[str, Any] | None,
    details: dict[str, Any],
    message: str,
) -> None:
    try:
        create_audit(
            event_type=event_type,
            user_id=extract_quote_actor_id(user),
            details=details,
            message=message,
        )
    except Exception:
        pass


def _serialize_item(item: QuoteItem) -> dict[str, Any]:
    return {
        "id": item.id,
        "item_type": item.item_type,
        "sku": item.sku,
        "name": item.name,
        "description": item.description,
        "quantity": item.quantity,
        "unit_price": item.unit_price,
        "line_total": item.line_total,
        "sort_order": item.sort_order,
        "source_table": item.source_table,
        "source_id": item.source_id,
    }


def _serialize_recipient(recipient: QuoteRecipient) -> dict[str, Any]:
    return {
        "id": recipient.id,
        "name": recipient.name,
        "email": recipient.email,
        "is_primary": bool(recipient.is_primary),
    }


def serialize_quote(quote: Quote, client: Client | None) -> dict[str, Any]:
    return {
        "id": quote.id,
        "quote_number": quote.quote_number,
        "client_id": quote.client_id,
        "client_name": client.name if client else None,
        "client_email": client.email if client else None,
        "client_phone": client.phone if client else None,
        "device_id": quote.device_id,
        "problem_description": quote.problem_description,
        "photos_received": quote.photos_received,
        "diagnosis": quote.diagnosis,
        "estimated_hours": quote.estimated_hours,
        "estimated_parts_cost": quote.estimated_parts_cost,
        "estimated_labor_cost": quote.estimated_labor_cost,
        "estimated_total": quote.estimated_total,
        "status": quote.status,
        "valid_until": quote.valid_until.isoformat() if quote.valid_until else None,
        "client_response": quote.client_response,
        "responded_at": quote.responded_at.isoformat() if quote.responded_at else None,
        "created_at": quote.created_at.isoformat() if quote.created_at else None,
        "updated_at": quote.updated_at.isoformat() if quote.updated_at else None,
        "items": [_serialize_item(item) for item in (quote.items or [])],
        "recipients": [_serialize_recipient(recipient) for recipient in (quote.recipients or [])],
    }


def get_quote_client(db: Session, quote: Quote) -> Client | None:
    if not quote.client_id:
        return None
    return db.query(Client).filter(Client.id == quote.client_id).first()


def serialize_quote_with_client(db: Session, quote: Quote) -> dict[str, Any]:
    return serialize_quote(quote, get_quote_client(db, quote))


def create_quote_from_payload(
    db: Session,
    payload: dict[str, Any],
    user: dict[str, Any] | None,
) -> dict[str, Any]:
    validate_quote_creation_payload(payload)
    client = resolve_quote_client(db, payload)
    quote_number = generate_quote_number(db)

    new_quote = build_quote_model(
        payload,
        quote_number=quote_number,
        client_id=client.id,
        created_by=extract_quote_actor_id(user),
    )

    db.add(new_quote)
    db.flush()

    _apply_quote_relations(
        new_quote,
        payload,
        client=client,
        apply_estimate_overrides_when_no_items=False,
    )

    _commit_quote(db, new_quote)

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


def update_quote_from_payload(
    db: Session,
    quote: Quote,
    payload: dict[str, Any],
    user: dict[str, Any] | None,
) -> dict[str, Any]:
    client = None
    if "client_id" in payload and payload.get("client_id"):
        client = assign_quote_client(db, quote, payload.get("client_id"))

    apply_quote_payload_updates(quote, payload)

    status_changed = False
    if "status" in payload:
        status_changed = apply_quote_status_transition(quote, payload.get("status"))

    client = client or get_quote_client(db, quote)
    _apply_quote_relations(
        quote,
        payload,
        client=client,
        apply_estimate_overrides_when_no_items=True,
    )

    _commit_quote(db, quote)

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

    return serialize_quote(quote, client)


def update_quote_status_from_payload(
    db: Session,
    quote: Quote,
    payload: dict[str, Any],
    user: dict[str, Any] | None,
) -> dict[str, Any]:
    apply_quote_status_transition(
        quote,
        payload.get("status"),
        client_response=payload.get("client_response")
        if payload.get("client_response") is not None
        else None,
    )

    _commit_quote(db, quote)

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


def _queue_quote_whatsapp_delivery(
    background_tasks: BackgroundTasks,
    quote: Quote,
    client: Client | None,
    send_whatsapp: bool,
) -> bool:
    if not send_whatsapp or not client or not client.phone:
        return False

    background_tasks.add_task(
        WhatsAppService().send_text,
        to_phone=client.phone,
        message=(
            f"Cotización {quote.quote_number}: total estimado ${quote.estimated_total or 0:,.0f} CLP. "
            f"Revisa tu correo para el detalle."
        ),
    )
    return True


def _emit_quote_saved_event(
    quote: Quote,
    client: Client | None,
    sent_to: list[str],
) -> None:
    try:
        event_bus.emit(
            Events.QUOTATION_SAVED,
            build_quote_saved_event_payload(quote, client, sent_to),
        )
    except Exception:
        pass


def send_quote_to_recipients(
    db: Session,
    quote: Quote,
    payload: dict[str, Any],
    *,
    background_tasks: BackgroundTasks,
    user: dict[str, Any] | None,
) -> dict[str, Any]:
    client = get_quote_client(db, quote)
    ensure_default_recipient(quote, client)

    recipient_emails = collect_quote_recipient_emails(quote)
    if not recipient_emails:
        raise HTTPException(status_code=400, detail="Quote has no recipients")

    custom_message = str(payload.get("message") or "").strip()
    delivery_content = build_quote_delivery_content(quote, client, custom_message)

    sent_to, failed_to = send_quote_email_batch(
        EmailService(),
        recipient_emails,
        delivery_content["subject"],
        delivery_content["html_content"],
    )

    whatsapp_queued = _queue_quote_whatsapp_delivery(
        background_tasks,
        quote,
        client,
        bool(payload.get("send_whatsapp", False)),
    )

    mark_quote_as_sent(quote)
    _commit_quote(db, quote)

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

    _emit_quote_saved_event(quote, client, sent_to)

    return {
        "quote": serialize_quote(quote, client),
        "sent_to": sent_to,
        "failed_to": failed_to,
        "whatsapp_queued": whatsapp_queued,
    }


def delete_quote_if_unlinked(db: Session, quote: Quote) -> dict[str, bool]:
    if count_linked_repairs(db, quote):
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar una cotización asociada a una OT",
        )

    db.delete(quote)
    db.commit()
    return {"ok": True}


def add_quote_item_to_quote(
    db: Session,
    quote: Quote,
    payload: dict[str, Any],
) -> dict[str, Any]:
    quote.items.append(build_quote_item(payload, sort_order=len(quote.items)))
    recalculate_quote_totals(quote)
    _commit_quote(db, quote)
    return serialize_quote_with_client(db, quote)


def update_quote_item_on_quote(
    db: Session,
    quote: Quote,
    item_id: int,
    payload: dict[str, Any],
) -> dict[str, Any]:
    item = get_quote_item_or_404(db, quote, item_id)
    update_quote_item_fields(item, payload)
    recalculate_quote_totals(quote)
    _commit_quote(db, quote)
    return serialize_quote_with_client(db, quote)


def delete_quote_item_from_quote(
    db: Session,
    quote: Quote,
    item_id: int,
) -> dict[str, Any]:
    item = get_quote_item_or_404(db, quote, item_id)
    db.delete(item)
    db.flush()
    recalculate_quote_totals(quote)
    _commit_quote(db, quote)
    return serialize_quote_with_client(db, quote)


def add_quote_recipient_to_quote(
    db: Session,
    quote: Quote,
    payload: dict[str, Any],
) -> dict[str, Any]:
    append_quote_recipient(quote, payload)
    _commit_quote(db, quote)
    return serialize_quote_with_client(db, quote)


def delete_quote_recipient_from_quote(
    db: Session,
    quote: Quote,
    recipient_id: int,
) -> dict[str, Any]:
    recipient = get_quote_recipient_or_404(db, quote, recipient_id)
    db.delete(recipient)
    db.flush()
    rebalance_quote_recipients(quote, get_quote_client(db, quote))
    _commit_quote(db, quote)
    return serialize_quote_with_client(db, quote)


def update_quote_item_fields(item: QuoteItem, payload: dict[str, Any]) -> None:
    if "item_type" in payload:
        item.item_type = str(payload.get("item_type") or item.item_type).strip().lower()
    if "sku" in payload:
        item.sku = payload.get("sku")
    if "name" in payload:
        item.name = str(payload.get("name") or item.name).strip()
    if "description" in payload:
        item.description = payload.get("description")
    if "quantity" in payload:
        item.quantity = to_float(payload.get("quantity"), item.quantity)
    if "unit_price" in payload:
        item.unit_price = to_float(payload.get("unit_price"), item.unit_price)
    if "line_total" in payload:
        item.line_total = to_float(payload.get("line_total"), item.line_total)
    else:
        item.recalculate_line_total()

    if "sort_order" in payload:
        item.sort_order = int(payload.get("sort_order") or item.sort_order)


def apply_quote_estimate_overrides(quote: Quote, payload: dict[str, Any]) -> None:
    if "estimated_parts_cost" in payload:
        quote.estimated_parts_cost = to_float(payload.get("estimated_parts_cost"), quote.estimated_parts_cost)
    if "estimated_labor_cost" in payload:
        quote.estimated_labor_cost = to_float(payload.get("estimated_labor_cost"), quote.estimated_labor_cost)
    if "estimated_total" in payload:
        quote.estimated_total = to_float(payload.get("estimated_total"), quote.estimated_total)


def get_quote_item_or_404(db: Session, quote: Quote, item_id: int) -> QuoteItem:
    item = (
        db.query(QuoteItem)
        .filter(QuoteItem.id == item_id, QuoteItem.quote_id == quote.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Quote item not found")
    return item


def get_quote_recipient_or_404(db: Session, quote: Quote, recipient_id: int) -> QuoteRecipient:
    recipient = (
        db.query(QuoteRecipient)
        .filter(QuoteRecipient.id == recipient_id, QuoteRecipient.quote_id == quote.id)
        .first()
    )
    if not recipient:
        raise HTTPException(status_code=404, detail="Quote recipient not found")
    return recipient


def append_quote_recipient(quote: Quote, payload: dict[str, Any]) -> QuoteRecipient:
    recipient = build_quote_recipient(payload, index=len(quote.recipients))
    if not recipient.email:
        raise HTTPException(status_code=400, detail="Campo requerido: email")

    if recipient.is_primary:
        for existing in quote.recipients:
            existing.is_primary = False

    quote.recipients.append(recipient)
    return recipient


def count_linked_repairs(db: Session, quote: Quote) -> int:
    return db.query(Repair).filter(Repair.quote_id == quote.id).count()


def rebalance_quote_recipients(quote: Quote, client: Client | None) -> None:
    if not quote.recipients:
        ensure_default_recipient(quote, client)
        return

    if any(bool(recipient.is_primary) for recipient in quote.recipients):
        return

    quote.recipients[0].is_primary = True
