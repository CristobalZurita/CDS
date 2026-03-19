"""Quote domain helpers (aditivo, sin romper endpoints existentes)."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.quote import Quote, QuoteItem, QuoteRecipient, QuoteStatus

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


def can_transition_status(current: str | None, new_status: str | None) -> bool:
    source = normalize_status(current)
    target = normalize_status(new_status)
    if source == target:
        return True
    return target in _STATUS_TRANSITIONS.get(source, set())


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
