from fastapi import APIRouter, HTTPException
from pathlib import Path
import json

router = APIRouter(prefix="/instruments", tags=["instruments"]) 

DATA_PATH = Path(__file__).resolve().parents[5] / "src" / "assets" / "data"

@router.get("/{instrument_id}")
async def get_instrument(instrument_id: str):
    with open(DATA_PATH / "instruments.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    instruments = data.get("instruments", [])
    inst = next((i for i in instruments if i.get("id") == instrument_id), None)
    if not inst:
        raise HTTPException(status_code=404, detail="Instrument not found")
    return inst

@router.get("/{instrument_id}/image")
async def get_instrument_image(instrument_id: str):
    # Return imagen_url as-is; frontend should handle relative paths
    with open(DATA_PATH / "instruments.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    instruments = data.get("instruments", [])
    inst = next((i for i in instruments if i.get("id") == instrument_id), None)
    if not inst:
        raise HTTPException(status_code=404, detail="Instrument not found")
    img = inst.get("imagen_url")
    if not img:
        raise HTTPException(status_code=404, detail="No image for instrument")
    return {"imagen_url": img}
