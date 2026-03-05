"""Quote domain helpers (aditivo, sin romper endpoints existentes)."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

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
