"""
API routes for diagnostic and quotation system
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional

# Avoid importing application schemas directly to keep router import lightweight in tests
from app.core.config import get_settings, Settings
from app.core.database import get_db
from app.core.ratelimit import limiter
from app.core.dependencies import get_current_user, require_permission
from app.models.diagnostic import Diagnostic
from app.models.quote import Quote, QuoteItem, QuoteRecipient, QuoteStatus
from app.models.client import Client
from app.models.repair import Repair
from app.services.logging_service import create_audit
from app.services.email_service import EmailService, build_email_html
from app.services.whatsapp_service import WhatsAppService
from app.services.event_system import event_bus, Events
from app.services.quote_management import (
    build_quote_item,
    build_quote_recipient,
    can_transition_status,
    normalize_status,
    parse_iso_date,
    recalculate_quote_totals,
    serialize_quote,
    to_float,
)
from app.services.reference_catalog_service import (
    get_applicable_faults_for_instrument,
    get_catalog_brands,
    get_catalog_faults,
    get_catalog_instrument,
    get_catalog_models_by_brand,
    get_reference_catalog,
)
from app.services.quotation_engine import calculate_fault_estimate
from datetime import datetime, timedelta

router = APIRouter(prefix="/diagnostic", tags=["diagnostic"])


def _reference_catalog() -> dict:
    return get_reference_catalog()


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
        if svc.has_permission(user_id, "quotes", action) or svc.has_permission(user_id, "diagnostics", action):
            return user

        raise HTTPException(
            status_code=403,
            detail=f"No tiene permiso para {action} en quotes/diagnostics",
        )

    return checker


@router.get("/instruments/brands")
async def get_brands():
    """Get all available instrument brands"""
    return get_catalog_brands()


@router.get("/instruments/models/{brand_id}")
async def get_models_by_brand(brand_id: str):
    """Get all models for a specific brand"""
    return get_catalog_models_by_brand(brand_id)


@router.get("/instruments/{instrument_id}")
async def get_instrument(instrument_id: str):
    """Get detailed information about a specific instrument"""
    instrument = get_catalog_instrument(instrument_id)
    if instrument:
        return instrument
    raise HTTPException(status_code=404, detail="Instrument not found")


@router.get("/faults")
async def get_all_faults():
    """Get all available faults"""
    return get_catalog_faults()


@router.get("/faults/applicable/{instrument_id}")
async def get_applicable_faults(instrument_id: str):
    """Get faults applicable to a specific instrument"""
    applicable_faults = get_applicable_faults_for_instrument(instrument_id)
    if not applicable_faults and not get_catalog_instrument(instrument_id):
        raise HTTPException(status_code=404, detail="Instrument not found")
    return applicable_faults


@router.post("/calculate")
@limiter.limit("10/minute")
async def calculate_diagnostic(
    diagnostic: dict,
    request: Request,
    settings: Settings = Depends(get_settings)
):
    """
    Calculate diagnostic quote based on instrument and faults

    The quote calculation follows these rules:
    1. If POWER fault is present, it takes precedence over all others
    2. Base price is sum of all fault prices
    3. Applied multipliers:
       - Instrument tier (brand tier complexity factor)
       - Equipment value (estimated value multiplier)
    """

    catalog = _reference_catalog()
    instrument = catalog["instruments_by_id"].get(diagnostic.get("equipment", {}).get("model"))

    if not instrument:
        raise HTTPException(status_code=404, detail="Instrument not found")

    brand = catalog["brands_by_id"].get(diagnostic.get("equipment", {}).get("brand"))

    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    estimate = calculate_fault_estimate(
        instrument=instrument,
        brand=brand,
        fault_ids=diagnostic.get("faults", []),
        faults_catalog=catalog["faults"],
        service_multipliers=settings.service_multipliers,
    )
    equipment_value = estimate["instrument_value_avg"]

    # Audit the diagnostic calculation (non-fatal)
    try:
        create_audit(
            event_type="diagnostic.calculate",
            user_id=None,
            details={
                "brand": brand.get("id"),
                "model": instrument.get("id"),
                "faults": estimate["effective_faults"],
                "final_cost": estimate["final_cost"],
            },
            message="Diagnostic calculated",
        )
    except Exception:
        pass

    return {
        "equipment_info": {"brand": brand["name"], "model": instrument["model"], "value": equipment_value},
        "faults": estimate["effective_faults"],
        "base_cost": estimate["base_total"],
        "complexity_factor": estimate["complexity_factor"],
        "value_factor": estimate["value_factor"],
        "final_cost": estimate["final_cost"],
    }


@router.get("/")
async def list_diagnostics(
    skip: int = 0,
    limit: int = 100,
    repair_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    List all diagnostics with optional filtering

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **repair_id**: Filter by repair ID (optional)
    """
    query = db.query(Diagnostic)

    if repair_id:
        query = query.filter(Diagnostic.repair_id == repair_id)

    diagnostics = query.order_by(Diagnostic.created_at.desc()).offset(skip).limit(limit).all()

    return [
        {
            "id": d.id,
            "repair_id": d.repair_id,
            "image_path": d.image_path,
            "ai_analysis": d.ai_analysis,
            "detected_faults": d.detected_faults,
            "ai_confidence": d.ai_confidence,
            "quote_total": d.quote_total,
            "quote_breakdown": d.quote_breakdown,
            "labor_hours": d.labor_hours,
            "notes": d.notes,
            "created_at": d.created_at.isoformat() if d.created_at else None,
            "updated_at": d.updated_at.isoformat() if d.updated_at else None,
        }
        for d in diagnostics
    ]


@router.get("/{diagnostic_id}")
async def get_diagnostic_by_id(diagnostic_id: int, db: Session = Depends(get_db)):
    """Get a specific diagnostic by ID"""
    diagnostic = db.query(Diagnostic).filter(Diagnostic.id == diagnostic_id).first()

    if not diagnostic:
        raise HTTPException(status_code=404, detail="Diagnostic not found")

    return {
        "id": diagnostic.id,
        "repair_id": diagnostic.repair_id,
        "image_path": diagnostic.image_path,
        "ai_analysis": diagnostic.ai_analysis,
        "detected_faults": diagnostic.detected_faults,
        "ai_confidence": diagnostic.ai_confidence,
        "quote_total": diagnostic.quote_total,
        "quote_breakdown": diagnostic.quote_breakdown,
        "labor_hours": diagnostic.labor_hours,
        "notes": diagnostic.notes,
        "created_at": diagnostic.created_at.isoformat() if diagnostic.created_at else None,
        "updated_at": diagnostic.updated_at.isoformat() if diagnostic.updated_at else None,
    }


@router.put("/{diagnostic_id}")
async def update_diagnostic(
    diagnostic_id: int,
    data: dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("diagnostics", "update"))
):
    """
    Update an existing diagnostic

    Updatable fields:
    - repair_id, image_path, ai_analysis, detected_faults
    - ai_confidence, quote_total, quote_breakdown, labor_hours, notes
    """
    diagnostic = db.query(Diagnostic).filter(Diagnostic.id == diagnostic_id).first()

    if not diagnostic:
        raise HTTPException(status_code=404, detail="Diagnostic not found")

    # Update allowed fields
    allowed_fields = [
        "repair_id", "image_path", "ai_analysis", "detected_faults",
        "ai_confidence", "quote_total", "quote_breakdown", "labor_hours", "notes"
    ]

    for field in allowed_fields:
        if field in data:
            setattr(diagnostic, field, data[field])

    db.commit()
    db.refresh(diagnostic)

    return {
        "id": diagnostic.id,
        "repair_id": diagnostic.repair_id,
        "image_path": diagnostic.image_path,
        "ai_analysis": diagnostic.ai_analysis,
        "detected_faults": diagnostic.detected_faults,
        "ai_confidence": diagnostic.ai_confidence,
        "quote_total": diagnostic.quote_total,
        "quote_breakdown": diagnostic.quote_breakdown,
        "labor_hours": diagnostic.labor_hours,
        "notes": diagnostic.notes,
        "created_at": diagnostic.created_at.isoformat() if diagnostic.created_at else None,
        "updated_at": diagnostic.updated_at.isoformat() if diagnostic.updated_at else None,
    }


@router.delete("/{diagnostic_id}")
async def delete_diagnostic(diagnostic_id: int, db: Session = Depends(get_db), user: dict = Depends(require_permission("diagnostics", "delete"))):
    """Delete a diagnostic by ID"""
    diagnostic = db.query(Diagnostic).filter(Diagnostic.id == diagnostic_id).first()

    if not diagnostic:
        raise HTTPException(status_code=404, detail="Diagnostic not found")

    db.delete(diagnostic)
    db.commit()

    return {"message": "Diagnostic deleted successfully", "id": diagnostic_id}


def _generate_quote_number(db: Session) -> str:
    """Generate unique quote number"""
    year = datetime.utcnow().strftime("%Y")
    last_quote = db.query(Quote).filter(
        Quote.quote_number.like(f"COT-{year}-%")
    ).order_by(Quote.id.desc()).first()

    if last_quote:
        try:
            last_num = int(last_quote.quote_number.split("-")[-1])
            next_num = last_num + 1
        except (ValueError, IndexError):
            next_num = 1
    else:
        next_num = 1

    return f"COT-{year}-{next_num:04d}"


def _get_quote_or_404(db: Session, quote_id: int) -> Quote:
    quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    return quote


def _resolve_quote_client(db: Session, payload: dict) -> Client:
    client_id = payload.get("client_id")
    if client_id:
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        return client

    client_email = str(payload.get("client_email") or "").strip().lower()
    client_name = str(payload.get("client_name") or "").strip()

    if not client_email:
        raise HTTPException(status_code=400, detail="Campo requerido: client_email o client_id")
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


def _replace_quote_items(quote: Quote, payload_items: list[dict]) -> None:
    quote.items.clear()
    for idx, payload in enumerate(payload_items):
        quote.items.append(build_quote_item(payload, sort_order=idx))


def _replace_quote_recipients(quote: Quote, payload_recipients: list[dict]) -> None:
    quote.recipients.clear()
    for idx, payload in enumerate(payload_recipients):
        recipient = build_quote_recipient(payload, index=idx)
        if recipient.email:
            quote.recipients.append(recipient)


def _ensure_default_recipient(quote: Quote, client: Client | None) -> None:
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


@router.get("/quotes")
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


def _quote_bucket(status: str | None) -> str:
    current = normalize_status(status)
    if current == QuoteStatus.PENDING:
        return "draft_pending"
    if current == QuoteStatus.SENT:
        return "waiting_response"
    return "closed"


@router.get("/quotes/board")
async def quote_board(
    skip: int = 0,
    limit: int = 200,
    status: Optional[str] = None,
    client_id: Optional[int] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db),
    user: dict = Depends(require_quote_permission("read")),
):
    """
    Tablero de cotizaciones por bloques de estado.
    Inspirado en el flujo de columnas (en curso / espera / cerradas).
    """
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
        bucket = _quote_bucket(quote.status)
        serialized = serialize_quote(quote, clients.get(quote.client_id))
        linked_repair = linked_repairs.get(quote.id)
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
            "open_total": status_counts[QuoteStatus.PENDING] + status_counts[QuoteStatus.SENT],
        },
        "board": board,
    }


@router.post("/quotes")
async def create_quote(
    quote_data: dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_quote_permission("create")),
):
    """
    Create a new quote from diagnostic data.

    Body:
    - client_name: Nombre del cliente (requerido)
    - client_email: Email del cliente (requerido)
    - client_phone: Teléfono (opcional)
    - problem_description: Descripción del problema (requerido)
    - estimated_total: Total estimado (requerido)
    - estimated_parts_cost: Costo de partes (opcional)
    - estimated_labor_cost: Costo de mano de obra (opcional)
    - diagnosis: Diagnóstico (opcional)
    """
    if not quote_data.get("problem_description"):
        raise HTTPException(status_code=400, detail="Campo requerido: problem_description")

    items_payload = quote_data.get("items") or []
    if not items_payload and quote_data.get("estimated_total") is None:
        raise HTTPException(
            status_code=400,
            detail="Campo requerido: estimated_total o items",
        )

    client = _resolve_quote_client(db, quote_data)

    # Crear cotización
    quote_number = _generate_quote_number(db)
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
        valid_until=parse_iso_date(quote_data.get("valid_until")) or (datetime.utcnow().date() + timedelta(days=30)),
        created_by=user_id,
    )

    db.add(new_quote)
    db.flush()

    if isinstance(items_payload, list) and items_payload:
        _replace_quote_items(new_quote, items_payload)
        recalculate_quote_totals(new_quote)

    recipients_payload = quote_data.get("recipients") or []
    if isinstance(recipients_payload, list) and recipients_payload:
        _replace_quote_recipients(new_quote, recipients_payload)
    _ensure_default_recipient(new_quote, client)

    db.commit()
    db.refresh(new_quote)

    # Audit
    try:
        create_audit(
            event_type="quote.created",
            user_id=user_id,
            details={
                "quote_id": new_quote.id,
                "quote_number": quote_number,
                "client_id": client.id,
                "estimated_total": new_quote.estimated_total,
            },
            message=f"Quote {quote_number} created",
        )
    except Exception:
        pass

    return serialize_quote(new_quote, client)


@router.get("/quotes/{quote_id}")
async def get_quote(
    quote_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_quote_permission("read")),
):
    """Get a specific quote by ID"""
    quote = _get_quote_or_404(db, quote_id)
    client = db.query(Client).filter(Client.id == quote.client_id).first()
    return serialize_quote(quote, client)


@router.put("/quotes/{quote_id}")
async def update_quote(
    quote_id: int,
    quote_data: dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_quote_permission("update")),
):
    quote = _get_quote_or_404(db, quote_id)

    if "client_id" in quote_data and quote_data.get("client_id"):
        client = db.query(Client).filter(Client.id == quote_data.get("client_id")).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        quote.client_id = client.id

    if "problem_description" in quote_data:
        quote.problem_description = quote_data.get("problem_description") or quote.problem_description
    if "photos_received" in quote_data:
        quote.photos_received = quote_data.get("photos_received")
    if "diagnosis" in quote_data:
        quote.diagnosis = quote_data.get("diagnosis")
    if "estimated_hours" in quote_data:
        quote.estimated_hours = to_float(quote_data.get("estimated_hours"), quote.estimated_hours or 0)
    if "valid_until" in quote_data:
        quote.valid_until = parse_iso_date(quote_data.get("valid_until"))
    if "client_response" in quote_data:
        quote.client_response = quote_data.get("client_response")
    if "responded_at" in quote_data:
        parsed_responded = parse_iso_date(quote_data.get("responded_at"))
        quote.responded_at = datetime.combine(parsed_responded, datetime.min.time()) if parsed_responded else None

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
        _replace_quote_items(quote, quote_data.get("items"))
        recalculate_quote_totals(quote)
        items_replaced = True

    if "recipients" in quote_data and isinstance(quote_data.get("recipients"), list):
        _replace_quote_recipients(quote, quote_data.get("recipients"))

    client = db.query(Client).filter(Client.id == quote.client_id).first()
    _ensure_default_recipient(quote, client)

    if not items_replaced:
        if "estimated_parts_cost" in quote_data:
            quote.estimated_parts_cost = to_float(quote_data.get("estimated_parts_cost"), quote.estimated_parts_cost)
        if "estimated_labor_cost" in quote_data:
            quote.estimated_labor_cost = to_float(quote_data.get("estimated_labor_cost"), quote.estimated_labor_cost)
        if "estimated_total" in quote_data:
            quote.estimated_total = to_float(quote_data.get("estimated_total"), quote.estimated_total)

    db.commit()
    db.refresh(quote)

    # Audit
    try:
        user_id = int(user.get("user_id")) if user and user.get("user_id") else None
        create_audit(
            event_type="quote.updated",
            user_id=user_id,
            details={
                "quote_id": quote.id,
                "quote_number": quote.quote_number,
                "status_changed": status_changed,
            },
            message=f"Quote {quote.quote_number} updated",
        )
    except Exception:
        pass

    return serialize_quote(quote, client)


@router.delete("/quotes/{quote_id}")
async def delete_quote(
    quote_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_quote_permission("update")),
):
    quote = _get_quote_or_404(db, quote_id)
    linked_repairs = db.query(Repair).filter(Repair.quote_id == quote.id).count()
    if linked_repairs:
        raise HTTPException(status_code=400, detail="No se puede eliminar una cotización asociada a una OT")

    db.delete(quote)
    db.commit()
    return {"ok": True}


@router.post("/quotes/{quote_id}/status")
async def update_quote_status(
    quote_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_quote_permission("approve")),
):
    quote = _get_quote_or_404(db, quote_id)
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
    client = db.query(Client).filter(Client.id == quote.client_id).first()

    try:
        user_id = int(user.get("user_id")) if user and user.get("user_id") else None
        create_audit(
            event_type="quote.status_changed",
            user_id=user_id,
            details={
                "quote_id": quote.id,
                "quote_number": quote.quote_number,
                "status": quote.status,
            },
            message=f"Quote {quote.quote_number} status changed to {quote.status}",
        )
    except Exception:
        pass

    return serialize_quote(quote, client)


@router.post("/quotes/{quote_id}/send")
async def send_quote(
    quote_id: int,
    payload: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: dict = Depends(require_quote_permission("update")),
):
    """
    Envío de cotización a destinatarios.
    - Si está en pending, pasa a sent.
    - Envía por email (best effort) y WhatsApp opcional.
    """
    quote = _get_quote_or_404(db, quote_id)
    client = db.query(Client).filter(Client.id == quote.client_id).first()
    _ensure_default_recipient(quote, client)

    recipient_emails = []
    for recipient in quote.recipients:
        email = str(recipient.email or "").strip().lower()
        if email and email not in recipient_emails:
            recipient_emails.append(email)

    if not recipient_emails:
        raise HTTPException(status_code=400, detail="Quote has no recipients")

    custom_message = str(payload.get("message") or "").strip()
    subject = f"Cotización {quote.quote_number} - Cirujano de Sintetizadores"
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

    email_service = EmailService()
    sent_to = []
    failed_to = []
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

    if quote.status == QuoteStatus.PENDING:
        quote.status = QuoteStatus.SENT

    db.commit()
    db.refresh(quote)

    try:
        user_id = int(user.get("user_id")) if user and user.get("user_id") else None
        create_audit(
            event_type="quote.sent",
            user_id=user_id,
            details={
                "quote_id": quote.id,
                "quote_number": quote.quote_number,
                "sent_to": sent_to,
                "failed_to": failed_to,
                "whatsapp_queued": whatsapp_queued,
            },
            message=f"Quote {quote.quote_number} sent",
        )
    except Exception:
        pass

    # Hook no destructivo para handlers existentes.
    try:
        event_bus.emit(
            Events.QUOTATION_SAVED,
            {
                "customer_email": (sent_to[0] if sent_to else (client.email if client else None)),
                "customer_name": client.name if client else "Cliente",
                "quotation_id": quote.quote_number,
                "instrument": "Servicio técnico",
                "min_price": quote.estimated_total or 0,
                "max_price": quote.estimated_total or 0,
            },
        )
    except Exception:
        pass

    return {
        "quote": serialize_quote(quote, client),
        "sent_to": sent_to,
        "failed_to": failed_to,
        "whatsapp_queued": whatsapp_queued,
    }


@router.post("/quotes/{quote_id}/items")
async def add_quote_item(
    quote_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_quote_permission("update")),
):
    quote = _get_quote_or_404(db, quote_id)
    sort_order = len(quote.items)
    quote.items.append(build_quote_item(payload, sort_order=sort_order))
    recalculate_quote_totals(quote)

    db.commit()
    db.refresh(quote)
    client = db.query(Client).filter(Client.id == quote.client_id).first()
    return serialize_quote(quote, client)


@router.put("/quotes/{quote_id}/items/{item_id}")
async def update_quote_item(
    quote_id: int,
    item_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_quote_permission("update")),
):
    quote = _get_quote_or_404(db, quote_id)
    item = (
        db.query(QuoteItem)
        .filter(QuoteItem.id == item_id, QuoteItem.quote_id == quote.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Quote item not found")

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

    recalculate_quote_totals(quote)
    db.commit()
    db.refresh(quote)
    client = db.query(Client).filter(Client.id == quote.client_id).first()
    return serialize_quote(quote, client)


@router.delete("/quotes/{quote_id}/items/{item_id}")
async def delete_quote_item(
    quote_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_quote_permission("update")),
):
    quote = _get_quote_or_404(db, quote_id)
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

    client = db.query(Client).filter(Client.id == quote.client_id).first()
    db.refresh(quote)
    return serialize_quote(quote, client)


@router.post("/quotes/{quote_id}/recipients")
async def add_quote_recipient(
    quote_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_quote_permission("update")),
):
    quote = _get_quote_or_404(db, quote_id)
    recipient = build_quote_recipient(payload, index=len(quote.recipients))
    if not recipient.email:
        raise HTTPException(status_code=400, detail="Campo requerido: email")

    if recipient.is_primary:
        for existing in quote.recipients:
            existing.is_primary = False

    quote.recipients.append(recipient)
    db.commit()
    db.refresh(quote)
    client = db.query(Client).filter(Client.id == quote.client_id).first()
    return serialize_quote(quote, client)


@router.delete("/quotes/{quote_id}/recipients/{recipient_id}")
async def delete_quote_recipient(
    quote_id: int,
    recipient_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_quote_permission("update")),
):
    quote = _get_quote_or_404(db, quote_id)
    recipient = (
        db.query(QuoteRecipient)
        .filter(QuoteRecipient.id == recipient_id, QuoteRecipient.quote_id == quote.id)
        .first()
    )
    if not recipient:
        raise HTTPException(status_code=404, detail="Quote recipient not found")

    db.delete(recipient)
    db.flush()
    if not quote.recipients:
        client = db.query(Client).filter(Client.id == quote.client_id).first()
        _ensure_default_recipient(quote, client)
    else:
        primary_exists = any(bool(r.is_primary) for r in quote.recipients)
        if not primary_exists and quote.recipients:
            quote.recipients[0].is_primary = True

    db.commit()
    db.refresh(quote)
    client = db.query(Client).filter(Client.id == quote.client_id).first()
    return serialize_quote(quote, client)
