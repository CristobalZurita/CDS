"""
Motor compartido para cotización/diagnóstico.

Consolida la lógica común entre:
- app.routers.diagnostic
- app.routers.quotation

Regla:
- El modo "faults" usa un único cálculo canónico.
- El modo "guided" conserva su lógica de bandas, pero vive aquí para no
  duplicarse ni quedar atrapado dentro del router.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


FALLBACK_TIER_MULTIPLIERS = {
    "legendary": 1.5,
    "professional": 1.3,
    "historic": 1.4,
    "boutique": 1.2,
    "specialized": 1.1,
    "standard": 1.0,
}

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


def apply_power_precedence(faults: List[str] | None) -> List[str]:
    normalized = list(faults or [])
    if "POWER" in normalized:
        return ["POWER"]
    return normalized


def build_fault_breakdown(fault_ids: List[str], faults_catalog: Dict[str, dict]) -> tuple[int, List[Dict[str, Any]]]:
    base_total = 0
    breakdown: List[Dict[str, Any]] = []
    for fault_id in fault_ids:
        fault = faults_catalog.get(fault_id)
        if not fault:
            continue
        price = int(fault.get("basePrice", 0))
        base_total += price
        breakdown.append(
            {
                "fault_id": fault_id,
                "name": fault.get("name", fault_id),
                "base_price": price,
            }
        )
    return base_total, breakdown


def instrument_value_average(instrument: dict) -> int:
    value_meta = instrument.get("valor_estimado") or {}
    value_min = _safe_int(instrument.get("valor_min") or value_meta.get("min"))
    value_max = _safe_int(instrument.get("valor_max") or value_meta.get("max"))
    if value_min and value_max:
        return (value_min + value_max) // 2
    return value_min or value_max or 0


def value_factor_from_average(avg_value: int) -> float:
    if avg_value > 5000000:
        return 2.0
    if avg_value > 2000000:
        return 1.6
    if avg_value > 500000:
        return 1.3
    return 1.0


def resolve_tier_multiplier(tier: str, service_multipliers: Optional[Dict[str, float]] = None) -> float:
    normalized_tier = str(tier or "standard").strip().lower() or "standard"
    if service_multipliers and normalized_tier in service_multipliers:
        return float(service_multipliers[normalized_tier])
    return float(FALLBACK_TIER_MULTIPLIERS.get(normalized_tier, 1.0))


def calculate_fault_estimate(
    *,
    instrument: dict,
    brand: dict,
    fault_ids: List[str],
    faults_catalog: Dict[str, dict],
    service_multipliers: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    effective_faults = apply_power_precedence(fault_ids)
    base_total, breakdown = build_fault_breakdown(effective_faults, faults_catalog)
    tier = str(brand.get("tier") or "standard")
    complexity_factor = resolve_tier_multiplier(tier, service_multipliers)
    instrument_value_avg = instrument_value_average(instrument)
    value_factor = value_factor_from_average(instrument_value_avg)
    final_cost = int(base_total * complexity_factor * value_factor)
    max_recommended = int(instrument_value_avg * 0.5) if instrument_value_avg else 999999999

    return {
        "tier": tier,
        "effective_faults": effective_faults,
        "breakdown": breakdown,
        "base_total": base_total,
        "complexity_factor": complexity_factor,
        "value_factor": value_factor,
        "final_cost": final_cost,
        "instrument_value_avg": instrument_value_avg,
        "max_recommended": max_recommended,
        "exceeds_recommendation": final_cost > max_recommended,
        "summary": {
            "mode": "faults",
            "blocked_by_power": "POWER" in fault_ids,
            "selected_symptom_count": len(fault_ids),
            "visual_issue_count": 0,
            "notes_present": False,
            "range_label": "Estimación referencial",
            "complexity_factor": complexity_factor,
            "value_factor": value_factor,
            "final_cost": final_cost,
        },
    }


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
    avg_value = instrument_value_average(instrument)
    if avg_value > 5000000:
        return {"avg": avg_value, "weight": 2}
    if avg_value > 2000000:
        return {"avg": avg_value, "weight": 1}
    return {"avg": avg_value, "weight": 0}


def _symptom_weight(guided_answers: Dict[str, Any], blocked_by_power: bool) -> Dict[str, int]:
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


def estimate_guided_range(
    *,
    instrument: dict,
    brand: dict,
    guided_answers: Optional[Dict[str, Any]] = None,
    selected_symptoms: Optional[List[str]] = None,
    customer_notes: Optional[str] = None,
    visual_issue_count: int = 0,
    marked_faults: Optional[List[str]] = None,
) -> Dict[str, Any]:
    guided_answers = guided_answers or {}
    selected_symptoms = [symptom for symptom in (selected_symptoms or []) if symptom]
    marked_faults = marked_faults or []

    keyboard_profile = _infer_keyboard_size(instrument)
    controls_profile = _controls_weight(instrument)
    value_profile = _value_weight(instrument)

    blocked_by_power = str(guided_answers.get("power") or "") == "no_power"
    symptom_weights = _symptom_weight(guided_answers, blocked_by_power)
    visual_issue_count = max(_safe_int(visual_issue_count), len(marked_faults))

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
    tier = str(brand.get("tier") or "standard")
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
            "notes_present": bool(str(customer_notes or "").strip()),
            "main_issue": str(guided_answers.get("power") or "review_required"),
            "range_label": "Estimación referencial",
        },
    }
