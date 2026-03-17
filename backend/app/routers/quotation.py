from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from app.services.event_system import event_bus, Events
from app.core.ratelimit import limiter
from app.core.config import settings
from app.services.reference_catalog_service import (
    get_applicable_faults_for_instrument,
    get_catalog_brands,
    get_catalog_faults,
    get_catalog_instrument,
    get_catalog_models_by_brand,
    get_reference_catalog,
)
from app.services.quotation_engine import calculate_fault_estimate, estimate_guided_range

router = APIRouter(prefix="/quotations", tags=["quotations"])


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


@router.get("/instruments/brands")
async def get_quotation_brands():
    return get_catalog_brands()


@router.get("/instruments/models/{brand_id}")
async def get_quotation_models_by_brand(brand_id: str):
    return get_catalog_models_by_brand(brand_id)


@router.get("/instruments/{instrument_id}")
async def get_quotation_instrument(instrument_id: str):
    instrument = get_catalog_instrument(instrument_id)
    if instrument:
        return instrument
    raise HTTPException(status_code=404, detail="Instrumento no encontrado")


@router.get("/faults")
async def get_quotation_faults():
    return get_catalog_faults()


@router.get("/faults/applicable/{instrument_id}")
async def get_quotation_applicable_faults(instrument_id: str):
    applicable_faults = get_applicable_faults_for_instrument(instrument_id)
    if not applicable_faults and not get_catalog_instrument(instrument_id):
        raise HTTPException(status_code=404, detail="Instrumento no encontrado")
    return applicable_faults


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
    instrument = catalog["instruments_by_id"].get(payload.instrument_id)
    if not instrument:
        raise HTTPException(status_code=404, detail="Instrumento no encontrado")

    brand = catalog["brands_by_id"].get(instrument.get('brand'))
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
    else:
        fault_estimate = calculate_fault_estimate(
            instrument=instrument,
            brand=brand,
            fault_ids=payload.faults,
            faults_catalog=catalog["faults"],
            service_multipliers=settings.service_multipliers,
        )
        tier = fault_estimate["tier"]
        breakdown = [
            FaultBreakdown(
                fault_id=item["fault_id"],
                name=item["name"],
                base_price=item["base_price"],
            )
            for item in fault_estimate["breakdown"]
        ]
        base_total = fault_estimate["base_total"]
        combined_factor = fault_estimate["complexity_factor"] * fault_estimate["value_factor"]
        multiplier = round(combined_factor, 2) if base_total > 0 else 1.0
        min_price = int(fault_estimate["final_cost"] * 0.8)
        max_price = int(fault_estimate["final_cost"] * 1.3)
        valor_avg = fault_estimate["instrument_value_avg"]
        max_recommended = fault_estimate["max_recommended"]
        exceeds = fault_estimate["exceeds_recommendation"]
        summary = fault_estimate["summary"]

    disclaimer_text = (
        "Esta cotización es solamente referencial y no representa en ningún caso el valor final real. "
        "Los equipos pueden fallar por causas distintas a las visibles o descritas por el cliente, "
        "y el valor definitivo sólo se confirma después de la revisión física en taller."
    )

    return QuotationResponse(
        instrument_id=payload.instrument_id,
        instrument_name=f"{brand.get('name')} {instrument.get('model')}",
        brand_name=brand.get('name'),
        tier=tier,
        base_total=base_total,
        multiplier=multiplier,
        min_price=min_price,
        max_price=max_price,
        breakdown=breakdown,
        instrument_value_avg=valor_avg,
        max_recommended=max_recommended,
        exceeds_recommendation=exceeds,
        disclaimer=disclaimer_text,
        summary=summary,
    )
