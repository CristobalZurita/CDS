from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from app.core.ratelimit import limiter
from app.core.config import settings
from app.services.reference_catalog_service import get_reference_catalog
from app.services.quotation_engine import (
    build_canonical_quotation_payload,
    calculate_fault_estimate,
    estimate_guided_range,
    resolve_catalog_instrument_brand,
)
from app.routers import quote_management_router, quotation_catalog_router

router = APIRouter(prefix="/quotations", tags=["quotations"])
router.include_router(quotation_catalog_router.build_router())
router.include_router(quote_management_router.build_router(), prefix="/quotes")


class QuotationRequest(BaseModel):
    instrument_id: str
    faults: List[str] = []
    guided_answers: Optional[Dict[str, Any]] = None
    selected_symptoms: List[str] = []
    customer_notes: Optional[str] = None
    visual_issue_count: int = 0
    marked_faults: List[str] = []
    turnstile_token: str | None = None


class FaultBreakdown(BaseModel):
    fault_id: str
    name: str
    base_price: int


class QuotationResponse(BaseModel):
    instrument_id: str
    instrument_name: str
    brand_name: str
    tier: str

    base_total: int
    multiplier: float
    min_price: int
    max_price: int

    breakdown: List[FaultBreakdown]

    instrument_value_avg: int
    max_recommended: int
    exceeds_recommendation: bool

    disclaimer: str
    summary: Dict[str, Any]

@router.post("/estimate", response_model=QuotationResponse)
@limiter.limit("10/minute")
async def estimate_quotation(
    payload: QuotationRequest,
    request: Request,
):
    from app.services.turnstile_service import verify_turnstile
    if not payload.turnstile_token or not verify_turnstile(payload.turnstile_token):
        raise HTTPException(status_code=400, detail="Captcha inválido")
    catalog = get_reference_catalog()
    instrument, brand = resolve_catalog_instrument_brand(
        catalog=catalog,
        instrument_id=payload.instrument_id,
    )
    if not instrument:
        raise HTTPException(status_code=404, detail="Instrumento no encontrado")
    if not brand:
        raise HTTPException(status_code=404, detail="Marca no encontrada")

    guided_mode = bool(payload.guided_answers)

    if guided_mode:
        guided_estimate = estimate_guided_range(
            instrument=instrument,
            brand=brand,
            guided_answers=payload.guided_answers,
            selected_symptoms=payload.selected_symptoms,
            customer_notes=payload.customer_notes,
            visual_issue_count=payload.visual_issue_count,
            marked_faults=payload.marked_faults,
        )
        tier = guided_estimate["tier"]
        multiplier = guided_estimate["multiplier"]
        breakdown = guided_estimate["breakdown"]
        base_total = guided_estimate["base_total"]
        min_price = guided_estimate["min_price"]
        max_price = guided_estimate["max_price"]
        valor_avg = guided_estimate["instrument_value_avg"]
        max_recommended = guided_estimate["max_recommended"]
        exceeds = guided_estimate["exceeds_recommendation"]
        summary = guided_estimate["summary"]
        estimate_payload = {
            "tier": tier,
            "multiplier": multiplier,
            "breakdown": breakdown,
            "base_total": base_total,
            "min_price": min_price,
            "max_price": max_price,
            "instrument_value_avg": valor_avg,
            "max_recommended": max_recommended,
            "exceeds_recommendation": exceeds,
            "summary": summary,
        }
    else:
        fault_estimate = calculate_fault_estimate(
            instrument=instrument,
            brand=brand,
            fault_ids=payload.faults,
            faults_catalog=catalog["faults"],
            service_multipliers=settings.service_multipliers,
        )
        estimate_payload = fault_estimate

    canonical_payload = build_canonical_quotation_payload(
        instrument_id=payload.instrument_id,
        instrument=instrument,
        brand=brand,
        estimate=estimate_payload,
    )
    return QuotationResponse(**canonical_payload)
