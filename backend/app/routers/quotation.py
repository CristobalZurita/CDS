from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import json
import re
from pathlib import Path
from app.services.event_system import event_bus, Events
from app.core.ratelimit import limiter

router = APIRouter(prefix="/quotations", tags=["quotations"])

# Load data from frontend data assets so quotation logic uses same dataset
# DATA_PATH should point to the frontend data folder within the project
# The module sits at backend/app/routers, so parents[3] resolves to the project root
DATA_PATH = Path(__file__).resolve().parents[3] / "src" / "assets" / "data"

def _load_json(name: str):
    try:
        with open(DATA_PATH / name, 'r', encoding='utf-8') as fh:
            return json.load(fh)
    except Exception:
        return {}

BRANDS = {b['id']: b for b in _load_json('brands.json').get('brands', [])}
INSTRUMENTS = {i['id']: i for i in _load_json('instruments.json').get('instruments', [])}
FAULTS = _load_json('faults.json').get('faults', {})

# Simple tier configuration (can be tuned later)
TIER_CONFIG = {
    'legendary': {'multiplier': 1.5},
    'professional': {'multiplier': 1.3},
    'historic': {'multiplier': 1.4},
    'boutique': {'multiplier': 1.2},
    'specialized': {'multiplier': 1.1},
    'standard': {'multiplier': 1.0},
}


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


_KEYBOARDLESS_TERMS = (
    "rack",
    "module",
    "desktop",
    "expander",
)

_RANGE_BANDS = (
    (0, 2, (40000, 55000)),
    (3, 4, (50000, 70000)),
    (5, 6, (65000, 85000)),
    (7, 8, (80000, 105000)),
    (9, 10, (95000, 125000)),
    (11, 999, (110000, 150000)),
)


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed


def _infer_keyboard_size(instrument: dict) -> dict:
    model = str(instrument.get("model") or instrument.get("modelo") or "").lower()
    instrument_type = str(instrument.get("type") or "").lower()
    haystack = f"{model} {instrument_type}"

    if any(term in haystack for term in _KEYBOARDLESS_TERMS):
        return {"has_keyboard": False, "key_count": 0, "size_weight": 0, "label": "sin teclado"}

    match = re.search(r"\b(25|32|37|49|61|73|76|88)\b", haystack)
    key_count = _safe_int(match.group(1), 61) if match else 61

    if key_count <= 37:
        return {"has_keyboard": True, "key_count": key_count, "size_weight": 1, "label": "teclado chico"}
    if key_count <= 61:
        return {"has_keyboard": True, "key_count": key_count, "size_weight": 2, "label": "teclado mediano"}
    return {"has_keyboard": True, "key_count": key_count, "size_weight": 3, "label": "teclado grande"}


def _controls_weight(instrument: dict) -> dict:
    components = instrument.get("components") or {}
    controls_count = (
        _safe_int(components.get("botones"))
        + _safe_int(components.get("faders"))
        + _safe_int(components.get("encoders_rotativos"))
    )

    if controls_count >= 40:
        return {"count": controls_count, "weight": 3}
    if controls_count >= 20:
        return {"count": controls_count, "weight": 2}
    if controls_count >= 8:
        return {"count": controls_count, "weight": 1}
    return {"count": controls_count, "weight": 0}


def _value_weight(instrument: dict) -> dict:
    value_meta = instrument.get("valor_estimado") or {}
    avg_value = 0
    if value_meta.get("min") and value_meta.get("max"):
        avg_value = (_safe_int(value_meta.get("min")) + _safe_int(value_meta.get("max"))) // 2
    else:
        avg_value = _safe_int(value_meta.get("min"))

    if avg_value > 5000000:
        return {"avg": avg_value, "weight": 2}
    if avg_value > 2000000:
        return {"avg": avg_value, "weight": 1}
    return {"avg": avg_value, "weight": 0}


def _symptom_weight(guided_answers: dict, blocked_by_power: bool) -> dict:
    weights = {
        "power": 0,
        "audio": 0,
        "keyboard": 0,
        "controls": 0,
        "display": 0,
        "connectivity": 0,
        "cosmetic": 0,
    }

    power_answer = str(guided_answers.get("power") or "")
    if power_answer == "no_power":
        weights["power"] = 4
    elif power_answer == "intermittent_power":
        weights["power"] = 3

    cosmetic_answer = str(guided_answers.get("cosmetic") or "")
    if cosmetic_answer in {"water_damage", "heavy_damage"}:
        weights["cosmetic"] = 2
    elif cosmetic_answer in {"cosmetic_damage", "oxidation"}:
        weights["cosmetic"] = 1

    if blocked_by_power:
        return weights

    audio_answer = str(guided_answers.get("audio") or "")
    if audio_answer == "no_audio":
        weights["audio"] = 2
    elif audio_answer in {"one_side", "distorted", "weak"}:
        weights["audio"] = 1

    keyboard_answer = str(guided_answers.get("keyboard") or "")
    if keyboard_answer == "multiple_keys":
        weights["keyboard"] = 2
    elif keyboard_answer in {"single_key", "stuck_keys"}:
        weights["keyboard"] = 1

    controls_answer = str(guided_answers.get("controls") or "")
    if controls_answer == "multiple_controls":
        weights["controls"] = 2
    elif controls_answer in {"single_button", "single_slider", "single_knob"}:
        weights["controls"] = 1

    display_answer = str(guided_answers.get("display") or "")
    if display_answer in {"no_display", "broken_display", "low_contrast"}:
        weights["display"] = 1

    connectivity_answer = str(guided_answers.get("connectivity") or "")
    if connectivity_answer not in {"", "none", "not_applicable"}:
        weights["connectivity"] = 1

    return weights


def _band_from_score(score: int) -> tuple[int, int]:
    for min_score, max_score, band in _RANGE_BANDS:
        if min_score <= score <= max_score:
            return band
    return _RANGE_BANDS[-1][2]


def _estimate_guided_range(request: QuotationRequest, instrument: dict, brand: dict) -> dict:
    guided_answers = request.guided_answers or {}
    keyboard_profile = _infer_keyboard_size(instrument)
    controls_profile = _controls_weight(instrument)
    value_profile = _value_weight(instrument)

    blocked_by_power = str(guided_answers.get("power") or "") == "no_power"
    symptom_weights = _symptom_weight(guided_answers, blocked_by_power)
    selected_symptoms = [symptom for symptom in request.selected_symptoms if symptom]
    visual_issue_count = max(_safe_int(request.visual_issue_count), len(request.marked_faults))

    score = (
        keyboard_profile["size_weight"]
        + controls_profile["weight"]
        + value_profile["weight"]
        + sum(symptom_weights.values())
        + min(len(selected_symptoms), 3)
        + min(visual_issue_count, 3)
    )

    if blocked_by_power:
        score += 1

    min_price, max_price = _band_from_score(score)

    tier = brand.get("tier", "standard")
    if tier in {"legendary", "professional", "historic"}:
        min_price = min(min_price + 5000, 130000)
        max_price = min(max_price + 10000, 150000)

    return {
        "tier": tier,
        "score": score,
        "min_price": min_price,
        "max_price": max_price,
        "base_total": min_price,
        "multiplier": 1.0,
        "breakdown": [],
        "instrument_value_avg": value_profile["avg"],
        "max_recommended": 0,
        "exceeds_recommendation": False,
        "summary": {
            "mode": "guided",
            "blocked_by_power": blocked_by_power,
            "size_label": keyboard_profile["label"],
            "key_count": keyboard_profile["key_count"],
            "has_keyboard": keyboard_profile["has_keyboard"],
            "controls_count": controls_profile["count"],
            "selected_symptom_count": len(selected_symptoms),
            "visual_issue_count": visual_issue_count,
            "notes_present": bool(str(request.customer_notes or "").strip()),
            "main_issue": str(guided_answers.get("power") or "review_required"),
            "range_label": "Estimación referencial",
        },
    }


@router.post("/estimate", response_model=QuotationResponse)
@limiter.limit("10/minute")
async def estimate_quotation(payload: QuotationRequest, request: Request):
    from app.services.turnstile_service import verify_turnstile
    if not payload.turnstile_token or not verify_turnstile(payload.turnstile_token):
        raise HTTPException(status_code=400, detail="Captcha inválido")
    instrument = INSTRUMENTS.get(payload.instrument_id)
    if not instrument:
        raise HTTPException(status_code=404, detail="Instrumento no encontrado")

    brand = BRANDS.get(instrument.get('brand'))
    if not brand:
        raise HTTPException(status_code=404, detail="Marca no encontrada")

    guided_mode = bool(payload.guided_answers)

    if guided_mode:
        guided_estimate = _estimate_guided_range(payload, instrument, brand)
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
        tier = brand.get('tier', 'standard')
        multiplier = TIER_CONFIG.get(tier, TIER_CONFIG['standard'])['multiplier']

        # Precedence: if POWER present, only consider POWER
        effective_faults = payload.faults
        if 'POWER' in payload.faults:
            effective_faults = ['POWER']

        breakdown = []
        base_total = 0
        for fid in effective_faults:
            f = FAULTS.get(fid)
            if not f:
                continue
            price = int(f.get('basePrice', 0))
            base_total += price
            breakdown.append(FaultBreakdown(fault_id=fid, name=f.get('name', fid), base_price=price))

        adjusted_total = int(base_total * multiplier)
        min_price = int(adjusted_total * 0.8)
        max_price = int(adjusted_total * 1.3)

        valor_min = instrument.get('valor_min') or instrument.get('valor_estimado', {}).get('min') or 0
        valor_max = instrument.get('valor_max') or instrument.get('valor_estimado', {}).get('max') or 0
        valor_avg = (valor_min + valor_max) // 2 if valor_min and valor_max else 0
        max_recommended = int(valor_avg * 0.5) if valor_avg else 999999999
        exceeds = max_price > max_recommended
        summary = {
            "mode": "faults",
            "blocked_by_power": "POWER" in payload.faults,
            "selected_symptom_count": len(payload.faults),
            "visual_issue_count": 0,
            "notes_present": False,
            "range_label": "Estimación referencial",
        }

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
