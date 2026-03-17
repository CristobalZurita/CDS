"""
Servicio unificado para el catalogo legacy de marcas, instrumentos y fallas.

Objetivo:
- evitar lecturas duplicadas de JSON en multiples routers,
- recargar automaticamente si los archivos cambian.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
CATALOG_FILES = {
    "brands": DATA_DIR / "brands.json",
    "instruments": DATA_DIR / "instruments.json",
    "faults": DATA_DIR / "faults.json",
}

_catalog_cache_signature: tuple[tuple[str, int | None], ...] | None = None
_catalog_cache_payload: Dict[str, Any] | None = None


def _file_signature(path: Path) -> int | None:
    try:
        return path.stat().st_mtime_ns
    except FileNotFoundError:
        return None


def _catalog_signature() -> tuple[tuple[str, int | None], ...]:
    return tuple((name, _file_signature(path)) for name, path in sorted(CATALOG_FILES.items()))


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)

def get_reference_catalog() -> Dict[str, Any]:
    """
    Retorna un snapshot unico del catalogo legacy.

    El cache se invalida automaticamente cuando cambia alguno de los archivos
    `backend/app/data/*.json`, evitando reinicios manuales para ver cambios.
    """
    global _catalog_cache_signature, _catalog_cache_payload

    signature = _catalog_signature()
    if _catalog_cache_payload is not None and signature == _catalog_cache_signature:
        return _catalog_cache_payload

    brands_data = _read_json(CATALOG_FILES["brands"])
    instruments_data = _read_json(CATALOG_FILES["instruments"])
    faults_data = _read_json(CATALOG_FILES["faults"])

    brands = [dict(item or {}) for item in brands_data.get("brands", [])]
    instruments = [dict(item or {}) for item in instruments_data.get("instruments", [])]
    faults = faults_data.get("faults", {})

    payload = {
        "brands": brands,
        "brands_by_id": {item.get("id"): item for item in brands if item.get("id")},
        "instruments": instruments,
        "instruments_by_id": {item.get("id"): item for item in instruments if item.get("id")},
        "faults": faults,
        "fault_categories": faults_data.get("categories", {}),
    }

    _catalog_cache_signature = signature
    _catalog_cache_payload = payload
    return payload


def get_catalog_brands() -> List[Dict[str, Any]]:
    return get_reference_catalog()["brands"]


def get_catalog_models_by_brand(brand_id: str) -> List[Dict[str, Any]]:
    brand_key = str(brand_id or "").strip()
    if not brand_key:
        return []
    return [
        instrument
        for instrument in get_reference_catalog()["instruments"]
        if instrument.get("brand") == brand_key
    ]


def get_catalog_instrument(instrument_id: str) -> Dict[str, Any] | None:
    return get_reference_catalog()["instruments_by_id"].get(instrument_id)


def get_catalog_faults() -> Dict[str, Any]:
    return get_reference_catalog()["faults"]


def get_applicable_faults_for_instrument(instrument_id: str) -> List[Dict[str, Any]]:
    catalog = get_reference_catalog()
    faults = catalog["faults"]
    instrument = catalog["instruments_by_id"].get(instrument_id)

    if not instrument:
        return []

    applicable_faults: Dict[str, Any] = {}
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
        if fault_id in faults:
            applicable_faults[fault_id] = faults[fault_id]

    components = instrument.get("components") or {}
    instrument_type = str(instrument.get("type") or "").lower()

    if "teclado" in instrument_type:
        for fault_id in ("KEYBOARD_DEAD_KEY", "KEYBOARD_STUCK_KEY"):
            if fault_id in faults:
                applicable_faults[fault_id] = faults[fault_id]

    if components.get("lcd"):
        for fault_id in ("LCD_DEAD", "LCD_LOW_CONTRAST"):
            if fault_id in faults:
                applicable_faults[fault_id] = faults[fault_id]

    if (components.get("encoders_rotativos") or 0) > 0 and "ENCODER_INTERMITTENT" in faults:
        applicable_faults["ENCODER_INTERMITTENT"] = faults["ENCODER_INTERMITTENT"]

    if (components.get("faders") or 0) > 0 and "FADER_INTERMITTENT" in faults:
        applicable_faults["FADER_INTERMITTENT"] = faults["FADER_INTERMITTENT"]

    if (components.get("botones") or 0) > 0:
        for fault_id in ("BUTTON_STUCK", "BUTTON_DEAD"):
            if fault_id in faults:
                applicable_faults[fault_id] = faults[fault_id]

    if components.get("usb") and "USB_NOT_RECOGNIZED" in faults:
        applicable_faults["USB_NOT_RECOGNIZED"] = faults["USB_NOT_RECOGNIZED"]

    if components.get("midi_din") and "MIDI_NOT_RECOGNIZED" in faults:
        applicable_faults["MIDI_NOT_RECOGNIZED"] = faults["MIDI_NOT_RECOGNIZED"]

    if components.get("aftertouch") and "AFTERTOUCH_BROKEN" in faults:
        applicable_faults["AFTERTOUCH_BROKEN"] = faults["AFTERTOUCH_BROKEN"]

    return list(applicable_faults.values())
