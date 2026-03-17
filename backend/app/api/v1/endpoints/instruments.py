from fastapi import APIRouter, HTTPException

from app.services.cloudinary_service import resolve_image_url
from app.services.reference_catalog_service import get_reference_catalog

router = APIRouter(prefix="/instruments", tags=["instruments"])

@router.get("/{instrument_id}")
async def get_instrument(instrument_id: str):
    inst = get_reference_catalog().get("instruments_by_id", {}).get(instrument_id)
    if not inst:
        raise HTTPException(status_code=404, detail="Instrument not found")
    return inst

@router.get("/{instrument_id}/image")
async def get_instrument_image(instrument_id: str):
    inst = get_reference_catalog().get("instruments_by_id", {}).get(instrument_id)
    if not inst:
        raise HTTPException(status_code=404, detail="Instrument not found")
    raw_image = inst.get("imagen_url")
    if raw_image:
        img = resolve_image_url(raw_image)
    elif inst.get("foto_principal"):
        img = resolve_image_url(f"/images/instrumentos/{inst.get('foto_principal')}.webp")
    else:
        img = None
    if not img:
        raise HTTPException(status_code=404, detail="No image for instrument")
    return {"imagen_url": img}
