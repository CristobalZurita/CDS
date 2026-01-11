from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import json
from pathlib import Path
from backend.app.services.event_system import event_bus, Events

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
    faults: List[str]


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


@router.post("/estimate", response_model=QuotationResponse)
async def estimate_quotation(request: QuotationRequest):
    instrument = INSTRUMENTS.get(request.instrument_id)
    if not instrument:
        raise HTTPException(status_code=404, detail="Instrumento no encontrado")

    brand = BRANDS.get(instrument.get('brand'))
    if not brand:
        raise HTTPException(status_code=404, detail="Marca no encontrada")

    tier = brand.get('tier', 'standard')
    multiplier = TIER_CONFIG.get(tier, TIER_CONFIG['standard'])['multiplier']

    # Precedence: if POWER present, only consider POWER
    effective_faults = request.faults
    if 'POWER' in request.faults:
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

    disclaimer_text = (
        "⚠️ IMPORTANTE - INFORMACIÓN DE COTIZACIÓN\n\n"
        "Esta cotización es INDICATIVA y NO VINCULANTE.\n\n"
        "• El precio final se confirma tras revisión presencial del equipo en nuestro taller.\n"
        "• El diagnóstico completo requiere abrir el instrumento, lo que puede revelar fallas "
        "adicionales no detectables externamente.\n"
        "• El presupuesto formal tiene un costo de $20.000 CLP, que es:\n"
        "  - ABONABLE: Se descuenta del total si decide proceder con la reparación\n"
        "  - NO REEMBOLSABLE: Queda como pago por diagnóstico si rechaza la reparación\n\n"
        "• Reparación de síntesis: Nuestro compromiso es que nunca cobramos más del 50% "
        "del valor de mercado actual del instrumento."
    )
    
    if exceeds:
        disclaimer_text += (
            f"\n\n⚠️ ATENCIÓN: El costo estimado (${max_price:,}) sobrepasa el 50% del valor "
            f"del instrumento (${max_recommended:,}). Considere si es rentable reparar versus comprar otro."
        )

    return QuotationResponse(
        instrument_id=request.instrument_id,
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
    )
