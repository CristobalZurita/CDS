"""
API routes for diagnostic and quotation system
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
import json
from pathlib import Path

# Avoid importing application schemas directly to keep router import lightweight in tests
from backend.app.core.config import get_settings, Settings
from backend.app.services.logging_service import create_audit

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
async def calculate_diagnostic(diagnostic: dict, settings: Settings = Depends(get_settings)):
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


@router.post("/quotes")
async def create_quote(quote: dict):
    """
    Create a new quote from diagnostic data

    TODO: Implement database storage and email sending
    """
    # TODO: Save to database
    # TODO: Send confirmation email
    raise HTTPException(status_code=501, detail="Quote creation not yet implemented")


@router.get("/quotes/{quote_id}")
async def get_quote(quote_id: int):
    """Get a specific quote by ID"""
    # TODO: Fetch from database
    raise HTTPException(status_code=501, detail="Quote retrieval not yet implemented")
