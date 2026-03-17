"""
Compatibilidad diagnóstica e interna.

El flujo público canónico del cotizador vive en quotation.py.
Este router mantiene cálculo legacy, CRUD de diagnósticos y compatibilidad
de rutas históricas bajo /diagnostic.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from typing import List, Optional

# Avoid importing application schemas directly to keep router import lightweight in tests
from app.core.config import get_settings, Settings
from app.core.database import get_db
from app.core.ratelimit import limiter
from app.core.dependencies import require_permission
from app.models.diagnostic import Diagnostic
from app.services.logging_service import create_audit
from app.services.reference_catalog_service import get_reference_catalog
from app.services.quotation_engine import calculate_fault_estimate
from app.routers import quote_management_router, quotation_catalog_router

router = APIRouter(prefix="/diagnostic", tags=["diagnostic"])
router.include_router(quotation_catalog_router.build_router(deprecated=True))
router.include_router(quote_management_router.build_router(deprecated=True), prefix="/quotes")


def _reference_catalog() -> dict:
    return get_reference_catalog()

@router.post("/calculate", deprecated=True)
@limiter.limit("10/minute")
async def calculate_diagnostic(
    diagnostic: dict,
    request: Request,
    settings: Settings = Depends(get_settings)
):
    """
    Compatibilidad legacy del cálculo diagnóstico.

    El cotizador público canónico usa /api/v1/quotations/estimate.

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
