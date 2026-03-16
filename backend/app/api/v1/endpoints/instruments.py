from fastapi import APIRouter, HTTPException
from pathlib import Path
import json

router = APIRouter(prefix="/instruments", tags=["instruments"]) 

DATA_FILE = Path(__file__).resolve().parents[3] / "data" / "instruments.json"


def load_instruments_data() -> dict:
    if not DATA_FILE.exists():
        return {"instruments": []}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

@router.get("/{instrument_id}")
async def get_instrument(instrument_id: str):
    data = load_instruments_data()
    instruments = data.get("instruments", [])
    inst = next((i for i in instruments if i.get("id") == instrument_id), None)
    if not inst:
        raise HTTPException(status_code=404, detail="Instrument not found")
    return inst

@router.get("/{instrument_id}/image")
async def get_instrument_image(instrument_id: str):
    data = load_instruments_data()
    instruments = data.get("instruments", [])
    inst = next((i for i in instruments if i.get("id") == instrument_id), None)
    if not inst:
        raise HTTPException(status_code=404, detail="Instrument not found")
    img = inst.get("imagen_url") or (
        f"/images/instrumentos/{inst.get('foto_principal')}.webp"
        if inst.get("foto_principal")
        else None
    )
    if not img:
        raise HTTPException(status_code=404, detail="No image for instrument")
    return {"imagen_url": img}
