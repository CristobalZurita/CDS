"""
API routes for diagnostic and quotation system
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from pathlib import Path

# Avoid importing application schemas directly to keep router import lightweight in tests
from app.core.config import get_settings, Settings
from app.core.database import get_db
from app.core.ratelimit import limiter
from app.core.dependencies import get_current_user, require_permission
from app.models.diagnostic import Diagnostic
from app.models.quote import Quote
from app.models.client import Client
from app.services.logging_service import create_audit
from datetime import datetime, timedelta

router = APIRouter(prefix="/diagnostic", tags=["diagnostic"])

# Load static data (resolve paths relative to project root)
_root = Path(__file__).resolve().parents[3]
data_dir = _root / "src" / "assets" / "data"
with open(data_dir / "brands.json", "r") as f:
    brands_data = json.load(f)

with open(data_dir / "instruments.json", "r") as f:
    instruments_data = json.load(f)

with open(data_dir / "faults.json", "r") as f:
    faults_data = json.load(f)


@router.get("/instruments/brands")
async def get_brands():
    """Get all available instrument brands"""
    return brands_data["brands"]


@router.get("/instruments/models/{brand_id}")
async def get_models_by_brand(brand_id: str):
    """Get all models for a specific brand"""
    models = [
        instrument
        for instrument in instruments_data["instruments"]
        if instrument["brand"] == brand_id
    ]
    return models


@router.get("/instruments/{instrument_id}")
async def get_instrument(instrument_id: str):
    """Get detailed information about a specific instrument"""
    for instrument in instruments_data["instruments"]:
        if instrument["id"] == instrument_id:
            return instrument
    raise HTTPException(status_code=404, detail="Instrument not found")


@router.get("/faults")
async def get_all_faults():
    """Get all available faults"""
    return faults_data["faults"]


@router.get("/faults/applicable/{instrument_id}")
async def get_applicable_faults(instrument_id: str):
    """Get faults applicable to a specific instrument"""
    # Find the instrument
    instrument = None
    for inst in instruments_data["instruments"]:
        if inst["id"] == instrument_id:
            instrument = inst
            break

    if not instrument:
        raise HTTPException(status_code=404, detail="Instrument not found")

    # Build list of applicable faults based on instrument components
    applicable_faults = {}

    # Always include general faults
    general_fault_ids = [
        "POWER",
        "POWER_UNSTABLE",
        "AUDIO_DISTORTED",
        "AUDIO_NO_OUTPUT",
        "AUDIO_WEAK",
        "COSMETIC_DAMAGE",
        "WATER_DAMAGE",
        "CAPACITOR_BLOWN",
        "CONNECTOR_LOOSE",
    ]

    for fault_id in general_fault_ids:
        if fault_id in faults_data["faults"]:
            applicable_faults[fault_id] = faults_data["faults"][fault_id]

    # Add component-specific faults based on instrument components
    components = instrument["components"]

    # Keyboard faults
    if "teclado" in instrument["type"].lower():
        keyboard_faults = ["KEYBOARD_DEAD_KEY", "KEYBOARD_STUCK_KEY"]
        for fault_id in keyboard_faults:
            if fault_id in faults_data["faults"]:
                applicable_faults[fault_id] = faults_data["faults"][fault_id]

    # LCD faults
    if components.get("lcd"):
        lcd_faults = ["LCD_DEAD", "LCD_LOW_CONTRAST"]
        for fault_id in lcd_faults:
            if fault_id in faults_data["faults"]:
                applicable_faults[fault_id] = faults_data["faults"][fault_id]

    # Control faults
    if components.get("encoders_rotativos", 0) > 0:
        if "ENCODER_INTERMITTENT" in faults_data["faults"]:
            applicable_faults["ENCODER_INTERMITTENT"] = faults_data["faults"][
                "ENCODER_INTERMITTENT"
            ]

    if components.get("faders", 0) > 0:
        if "FADER_INTERMITTENT" in faults_data["faults"]:
            applicable_faults["FADER_INTERMITTENT"] = faults_data["faults"][
                "FADER_INTERMITTENT"
            ]

    if components.get("botones", 0) > 0:
        button_faults = ["BUTTON_STUCK", "BUTTON_DEAD"]
        for fault_id in button_faults:
            if fault_id in faults_data["faults"]:
                applicable_faults[fault_id] = faults_data["faults"][fault_id]

    # Connectivity faults
    if components.get("usb"):
        if "USB_NOT_RECOGNIZED" in faults_data["faults"]:
            applicable_faults["USB_NOT_RECOGNIZED"] = faults_data["faults"][
                "USB_NOT_RECOGNIZED"
            ]

    if components.get("midi_din"):
        if "MIDI_NOT_RECOGNIZED" in faults_data["faults"]:
            applicable_faults["MIDI_NOT_RECOGNIZED"] = faults_data["faults"][
                "MIDI_NOT_RECOGNIZED"
            ]

    # Aftertouch
    if components.get("aftertouch"):
        if "AFTERTOUCH_BROKEN" in faults_data["faults"]:
            applicable_faults["AFTERTOUCH_BROKEN"] = faults_data["faults"][
                "AFTERTOUCH_BROKEN"
            ]

    return list(applicable_faults.values())


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

    # Find the instrument
    instrument = None
    for inst in instruments_data["instruments"]:
        if inst["id"] == diagnostic.get("equipment", {}).get("model"):
            instrument = inst
            break

    if not instrument:
        raise HTTPException(status_code=404, detail="Instrument not found")

    # Find the brand
    brand = None
    for b in brands_data["brands"]:
        if b["id"] == diagnostic.get("equipment", {}).get("brand"):
            brand = b
            break

    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    # Check for precedence faults (POWER)
    effective_faults = diagnostic.get("faults", [])
    if "POWER" in effective_faults:
        effective_faults = ["POWER"]

    # Calculate base cost
    base_cost = 0
    for fault_id in effective_faults:
        if fault_id in faults_data["faults"]:
            fault = faults_data["faults"][fault_id]
            base_cost += fault.get("basePrice", 0)

    # Get complexity factor from settings
    complexity_factor = settings.service_multipliers.get(brand.get("tier"), 1.0)

    # Get value factor based on equipment value
    equipment_value = instrument["valor_estimado"]["min"]
    value_factor = 1.0

    if equipment_value > 5000000:
        value_factor = 2.0
    elif equipment_value > 2000000:
        value_factor = 1.6
    elif equipment_value > 500000:
        value_factor = 1.3

    # Calculate final cost
    final_cost = int(base_cost * complexity_factor * value_factor)

    # Audit the diagnostic calculation (non-fatal)
    try:
        create_audit(
            event_type="diagnostic.calculate",
            user_id=None,
            details={
                "brand": brand.get("id"),
                "model": instrument.get("id"),
                "faults": effective_faults,
                "final_cost": final_cost,
            },
            message="Diagnostic calculated",
        )
    except Exception:
        pass

    return {
        "equipment_info": {"brand": brand["name"], "model": instrument["model"], "value": equipment_value},
        "faults": effective_faults,
        "base_cost": base_cost,
        "complexity_factor": complexity_factor,
        "value_factor": value_factor,
        "final_cost": final_cost,
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


@router.post("/quotes")
async def create_quote(
    quote_data: dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("diagnostics", "create"))
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
    # Validar campos requeridos
    required_fields = ["client_name", "client_email", "problem_description", "estimated_total"]
    for field in required_fields:
        if field not in quote_data or not quote_data[field]:
            raise HTTPException(status_code=400, detail=f"Campo requerido: {field}")

    # Buscar o crear cliente
    client = db.query(Client).filter(Client.email == quote_data["client_email"]).first()
    if not client:
        client = Client(
            name=quote_data["client_name"],
            email=quote_data["client_email"],
            phone=quote_data.get("client_phone")
        )
        db.add(client)
        db.commit()
        db.refresh(client)

    # Crear cotización
    quote_number = _generate_quote_number(db)
    user_id = int(user.get("user_id")) if user and user.get("user_id") else None

    new_quote = Quote(
        quote_number=quote_number,
        client_id=client.id,
        problem_description=quote_data["problem_description"],
        diagnosis=quote_data.get("diagnosis"),
        estimated_parts_cost=quote_data.get("estimated_parts_cost", 0),
        estimated_labor_cost=quote_data.get("estimated_labor_cost", 0),
        estimated_total=quote_data["estimated_total"],
        status="pending",
        valid_until=datetime.utcnow().date() + timedelta(days=30),
        created_by=user_id
    )

    db.add(new_quote)
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
                "estimated_total": new_quote.estimated_total
            },
            message=f"Quote {quote_number} created"
        )
    except Exception:
        pass

    return {
        "id": new_quote.id,
        "quote_number": new_quote.quote_number,
        "client_id": new_quote.client_id,
        "client_name": client.name,
        "client_email": client.email,
        "problem_description": new_quote.problem_description,
        "diagnosis": new_quote.diagnosis,
        "estimated_parts_cost": new_quote.estimated_parts_cost,
        "estimated_labor_cost": new_quote.estimated_labor_cost,
        "estimated_total": new_quote.estimated_total,
        "status": new_quote.status,
        "valid_until": new_quote.valid_until.isoformat() if new_quote.valid_until else None,
        "created_at": new_quote.created_at.isoformat() if new_quote.created_at else None
    }


@router.get("/quotes/{quote_id}")
async def get_quote(
    quote_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("diagnostics", "read"))
):
    """Get a specific quote by ID"""
    quote = db.query(Quote).filter(Quote.id == quote_id).first()

    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")

    client = db.query(Client).filter(Client.id == quote.client_id).first()

    return {
        "id": quote.id,
        "quote_number": quote.quote_number,
        "client_id": quote.client_id,
        "client_name": client.name if client else None,
        "client_email": client.email if client else None,
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
        "updated_at": quote.updated_at.isoformat() if quote.updated_at else None
    }
