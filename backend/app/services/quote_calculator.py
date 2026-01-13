"""
Quote Calculator Service
Servicio para calcular cotizaciones basadas en diagnósticos
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from backend.app.schemas.diagnostic import FaultBreakdown


# Cargar datos estáticos
_root = Path(__file__).resolve().parents[3]
data_dir = _root / "src" / "assets" / "data"


def _load_json(filename: str) -> dict:
    """Carga archivo JSON desde el directorio de datos"""
    try:
        with open(data_dir / filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


# Datos cargados al inicio
_brands_data = _load_json("brands.json")
_instruments_data = _load_json("instruments.json")
_faults_data = _load_json("faults.json")

# Caches para acceso rápido
_BRANDS = {b["id"]: b for b in _brands_data.get("brands", [])}
_INSTRUMENTS = {i["id"]: i for i in _instruments_data.get("instruments", [])}
_FAULTS = _faults_data.get("faults", {})

# Configuración de tiers
TIER_MULTIPLIERS = {
    "legendary": 1.5,
    "professional": 1.3,
    "historic": 1.4,
    "boutique": 1.2,
    "specialized": 1.1,
    "standard": 1.0,
}

# Configuración de factores de valor
VALUE_THRESHOLDS = [
    (5000000, 2.0),    # > 5M CLP: multiplicador 2.0
    (2000000, 1.6),    # > 2M CLP: multiplicador 1.6
    (500000, 1.3),     # > 500K CLP: multiplicador 1.3
    (0, 1.0),          # resto: multiplicador 1.0
]

# Constantes
DIAGNOSTIC_FEE = 20000  # Costo de diagnóstico en CLP (centavos: 2000000)
MAX_VALUE_PERCENTAGE = 0.5  # Máximo 50% del valor del instrumento


def get_instrument(instrument_id: str) -> Optional[Dict[str, Any]]:
    """Obtiene información de un instrumento"""
    return _INSTRUMENTS.get(instrument_id)


def get_brand(brand_id: str) -> Optional[Dict[str, Any]]:
    """Obtiene información de una marca"""
    return _BRANDS.get(brand_id)


def get_fault(fault_id: str) -> Optional[Dict[str, Any]]:
    """Obtiene información de una falla"""
    return _FAULTS.get(fault_id)


def get_value_multiplier(instrument_value: int) -> float:
    """
    Calcula el multiplicador basado en el valor del instrumento

    Args:
        instrument_value: Valor del instrumento en CLP

    Returns:
        Multiplicador de valor
    """
    for threshold, multiplier in VALUE_THRESHOLDS:
        if instrument_value > threshold:
            return multiplier
    return 1.0


def calculate_labor_hours(faults: List[str]) -> int:
    """
    Estima horas de trabajo basadas en las fallas

    Args:
        faults: Lista de IDs de fallas

    Returns:
        Horas de trabajo estimadas
    """
    base_hours = 2  # Mínimo 2 horas de diagnóstico

    for fault_id in faults:
        fault = get_fault(fault_id)
        if fault:
            # Cada falla añade horas según su severidad
            severity = fault.get("severity", 50)
            hours_per_fault = max(1, severity // 25)  # 1-4 horas por falla
            base_hours += hours_per_fault

    return min(base_hours, 40)  # Máximo 40 horas


def calculate_quote(
    instrument_id: str,
    brand_id: str,
    faults: List[str]
) -> Dict[str, Any]:
    """
    Calcula cotización basada en instrumento y fallas

    Args:
        instrument_id: ID del instrumento
        brand_id: ID de la marca
        faults: Lista de IDs de fallas

    Returns:
        Dict con información de la cotización

    Raises:
        ValueError: Si no se encuentra el instrumento o la marca
    """
    # Validar instrumento
    instrument = get_instrument(instrument_id)
    if not instrument:
        raise ValueError(f"Instrumento no encontrado: {instrument_id}")

    # Validar marca
    brand = get_brand(brand_id)
    if not brand:
        raise ValueError(f"Marca no encontrada: {brand_id}")

    # Obtener tier y multiplicador de complejidad
    tier = brand.get("tier", "standard")
    complexity_multiplier = TIER_MULTIPLIERS.get(tier, 1.0)

    # Manejar precedencia de fallas (POWER anula todas las demás)
    effective_faults = faults
    if "POWER" in faults:
        effective_faults = ["POWER"]

    # Calcular costo base
    base_cost = 0
    breakdown: List[FaultBreakdown] = []

    for fault_id in effective_faults:
        fault = get_fault(fault_id)
        if fault:
            price = int(fault.get("basePrice", 0))
            base_cost += price
            breakdown.append(FaultBreakdown(
                fault_id=fault_id,
                name=fault.get("name", fault_id),
                base_price=price,
                severity=fault.get("severity")
            ))

    # Obtener valor del instrumento
    valor_estimado = instrument.get("valor_estimado", {})
    valor_min = valor_estimado.get("min", 0)
    valor_max = valor_estimado.get("max", 0)
    instrument_value = (valor_min + valor_max) // 2 if valor_min and valor_max else 0

    # Calcular multiplicador de valor
    value_multiplier = get_value_multiplier(instrument_value)

    # Calcular costo ajustado
    adjusted_cost = int(base_cost * complexity_multiplier * value_multiplier)

    # Calcular rangos de precio (±20-30%)
    min_price = int(adjusted_cost * 0.8)
    max_price = int(adjusted_cost * 1.3)

    # Calcular horas de trabajo
    labor_hours = calculate_labor_hours(effective_faults)

    # Validar contra el 50% del valor del instrumento
    max_recommended = int(instrument_value * MAX_VALUE_PERCENTAGE) if instrument_value else 999999999
    exceeds_recommendation = max_price > max_recommended

    # Generar disclaimer
    disclaimer = (
        "⚠️ IMPORTANTE - INFORMACIÓN DE COTIZACIÓN\n\n"
        "Esta cotización es INDICATIVA y NO VINCULANTE.\n\n"
        "• El precio final se confirma tras revisión presencial del equipo en nuestro taller.\n"
        "• El diagnóstico completo requiere abrir el instrumento, lo que puede revelar fallas "
        "adicionales no detectables externamente.\n"
        f"• El presupuesto formal tiene un costo de ${DIAGNOSTIC_FEE:,} CLP, que es:\n"
        "  - ABONABLE: Se descuenta del total si decide proceder con la reparación\n"
        "  - NO REEMBOLSABLE: Queda como pago por diagnóstico si rechaza la reparación\n\n"
        "• Reparación de síntesis: Nuestro compromiso es que nunca cobramos más del 50% "
        "del valor de mercado actual del instrumento."
    )

    if exceeds_recommendation:
        disclaimer += (
            f"\n\n⚠️ ATENCIÓN: El costo estimado (${max_price:,} CLP) sobrepasa el 50% del valor "
            f"del instrumento (${max_recommended:,} CLP). Considere si es rentable reparar versus comprar otro."
        )

    return {
        "equipment_info": {
            "brand": brand["name"],
            "model": instrument.get("model", ""),
            "value": instrument_value,
            "tier": tier,
        },
        "faults": effective_faults,
        "base_cost": base_cost,
        "complexity_multiplier": complexity_multiplier,
        "value_multiplier": value_multiplier,
        "adjusted_cost": adjusted_cost,
        "min_price": min_price,
        "max_price": max_price,
        "labor_hours": labor_hours,
        "breakdown": [item.dict() for item in breakdown],
        "max_recommended": max_recommended,
        "exceeds_recommendation": exceeds_recommendation,
        "disclaimer": disclaimer,
    }
