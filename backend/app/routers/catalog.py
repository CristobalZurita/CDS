"""
Catálogo de instrumentos desde keyboards_database.json.

GET /catalog/brands                → lista de marcas únicas
GET /catalog/models/{brand_id}     → modelos de una marca
GET /catalog/faults/{instrument_key} → zonas de falla de un modelo
POST /catalog/quote                → cotización: JSON-first, IA solo como fallback

Lógica static-first: si el modelo y la falla están en el JSON → 0 tokens.
La IA solo se invoca cuando el modelo es desconocido o la falla no mapea a ninguna zona.
"""

import json
from functools import lru_cache
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/catalog", tags=["catalog"])

_DB_PATH = Path(__file__).parent.parent.parent / "keyboards_database.json"


@lru_cache(maxsize=1)
def _load_db() -> dict:
    with open(_DB_PATH, encoding="utf-8") as f:
        return json.load(f)


# ── Marcas ────────────────────────────────────────────────────────────────────

@router.get("/brands")
def get_brands():
    """Lista de marcas únicas, ordenadas alfabéticamente."""
    db = _load_db()
    seen: dict[str, dict] = {}
    for entry in db.values():
        brand = entry.get("brand", "").strip()
        if brand and brand not in seen:
            seen[brand] = {
                "id": brand.lower().replace(" ", "_"),
                "name": brand,
            }
    return sorted(seen.values(), key=lambda x: x["name"])


# ── Modelos ───────────────────────────────────────────────────────────────────

@router.get("/models/{brand_id}")
def get_models(brand_id: str):
    """Modelos de una marca (brand_id es la forma normalizada, e.g. 'korg')."""
    db = _load_db()
    result = []
    for key, entry in db.items():
        brand_norm = entry.get("brand", "").lower().replace(" ", "_")
        if brand_norm == brand_id.lower():
            result.append({
                "id": key,
                "model": entry.get("model", key),
                "type": entry.get("type", ""),
                "keys": entry.get("keys", 0),
                "image": entry.get("image", ""),
                "complexity": entry.get("complexity", "media"),
                "precio_usd": entry.get("precio_usd_mercado", []),
            })
    if not result:
        return []
    return sorted(result, key=lambda x: x["model"])


# ── Zonas de falla ────────────────────────────────────────────────────────────

@router.get("/faults/{instrument_key}")
def get_faults(instrument_key: str):
    """
    Zonas de falla de un instrumento.
    Cada zona incluye fallas_comunes como sub-lista para la UI.
    """
    db = _load_db()
    entry = db.get(instrument_key)
    if not entry:
        raise HTTPException(status_code=404, detail="Instrumento no encontrado en catálogo")
    return [
        {
            "id": zone["id"],
            "name": zone.get("label", zone["id"]),
            "cobro_base": zone.get("cobro_base", 20000),
            "fallas_comunes": zone.get("fallas_comunes", []),
        }
        for zone in entry.get("fault_zones", [])
    ]


# ── Cotización ────────────────────────────────────────────────────────────────

_COMPLEXITY_MULT = {
    "baja": 1.0,
    "media": 1.0,
    "alta": 1.2,
    "muy_alta": 1.5,
}

_AI_SYSTEM_PROMPT = """
Eres el asistente técnico de CDS (Cirujano de Sintetizadores), Valparaíso, Chile.
Técnico trabaja SOLO. Jornada real 4-6h/día. Multiplica tiempos de internet × 3.
Calcula el derecho a revisión en CLP (mínimo siempre 20000).
Responde SOLO con JSON válido, sin texto adicional:
{"min_price": <int>, "max_price": <int>, "final_cost": <int>, "complexity": "<baja|media|alta|muy_alta>", "tiempo_estimado": "<rango>", "disclaimer": "<frase breve>"}
""".strip()


class QuoteRequest(BaseModel):
    instrument_id: Optional[str] = ""   # key en el JSON, vacío si no encontrado
    faults: list[str] = []              # ids de fault_zone seleccionadas
    brand: Optional[str] = ""           # manual si instrumento no está en JSON
    model: Optional[str] = ""           # manual si instrumento no está en JSON
    description: Optional[str] = ""     # descripción libre adicional
    turnstile_token: Optional[str] = None


@router.post("/quote")
def calculate_quote(payload: QuoteRequest):
    """
    Cotización inteligente.
    - Si el modelo está en el JSON y las fallas mapean a zonas conocidas → respuesta estática (0 tokens IA).
    - Si el modelo está en el JSON pero alguna falla es libre → IA con contexto del JSON (tokens reducidos).
    - Si el modelo no está en el JSON → IA completa.
    """
    db = _load_db()
    entry = db.get(payload.instrument_id or "") if payload.instrument_id else None

    # ── Camino estático ───────────────────────────────────────────────────────
    if entry and payload.faults:
        zones_by_id = {z["id"]: z for z in entry.get("fault_zones", [])}
        matched = [zones_by_id[f] for f in payload.faults if f in zones_by_id]

        if matched:
            cobro = max(z.get("cobro_base", 20000) for z in matched)
            complexity = entry.get("complexity", "media")
            mult = _COMPLEXITY_MULT.get(complexity, 1.0)
            min_price = max(20000, cobro)
            max_price = max(min_price, int(cobro * mult))
            usd = entry.get("precio_usd_mercado", [0, 0])

            return {
                "from_db": True,
                "min_price": min_price,
                "max_price": max_price,
                "final_cost": min_price,
                "complexity": complexity,
                "valor_usd_min": usd[0] if len(usd) > 0 else 0,
                "valor_usd_max": usd[1] if len(usd) > 1 else 0,
                "fallas_seleccionadas": [z.get("label", z["id"]) for z in matched],
                "disclaimer": (
                    "Estimación preliminar basada en nuestro historial de reparaciones. "
                    "El costo final se confirma tras la revisión presencial en el taller."
                ),
                "summary": {
                    "complexity_factor": mult,
                    "value_factor": 1.0,
                    "final_cost": min_price,
                },
            }

    # ── Camino IA ─────────────────────────────────────────────────────────────
    from app.core.llm_cascade import AllModelsExhaustedError, query_json

    brand = entry.get("brand", payload.brand or "") if entry else (payload.brand or "")
    model = entry.get("model", payload.model or "") if entry else (payload.model or "")
    falla_txt = (
        payload.description.strip()
        or ", ".join(payload.faults)
        or "No especificada"
    )

    # Si tenemos datos del JSON, los incluimos como contexto para reducir tokens
    context = ""
    if entry:
        usd = entry.get("precio_usd_mercado", [0, 0])
        context = (
            f"DATOS CONOCIDOS:\n"
            f"- Complejidad catalogada: {entry.get('complexity', 'media')}\n"
            f"- Valor mercado estimado: USD {usd[0] if usd else 0}–{usd[1] if len(usd) > 1 else 0}\n\n"
        )

    user_prompt = (
        f"{context}"
        f"Equipo: {brand} {model}\n"
        f"Falla reportada: {falla_txt}\n\n"
        f"Responde SOLO con el JSON indicado."
    )

    try:
        result = query_json(user_prompt, _AI_SYSTEM_PROMPT)
        result["from_db"] = False
        result.setdefault("min_price", 20000)
        result.setdefault("max_price", result.get("min_price", 20000))
        result.setdefault("final_cost", result["min_price"])
        result.setdefault("summary", {
            "complexity_factor": 1.0,
            "value_factor": 1.0,
            "final_cost": result["final_cost"],
        })
        return result
    except AllModelsExhaustedError:
        raise HTTPException(
            status_code=503,
            detail="Servicio de cotización IA temporalmente no disponible. Intenta en unos minutos.",
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
