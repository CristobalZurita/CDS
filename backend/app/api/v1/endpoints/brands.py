from fastapi import APIRouter
from typing import List

from app.services.reference_catalog_service import get_reference_catalog

router = APIRouter(prefix="/brands", tags=["brands"])

@router.get("/", response_model=List[dict])
async def list_brands():
    """Return list of brands sorted A-Z by name"""
    brands = get_reference_catalog().get("brands", [])
    sorted_brands = sorted(brands, key=lambda b: b.get("name", "").lower())
    # Return minimal fields
    return [{"id": b["id"], "name": b["name"], "tier": b.get("tier")} for b in sorted_brands]

@router.get("/{brand_id}/models", response_model=List[dict])
async def list_models_by_brand(brand_id: str):
    """Return instruments for a given brand with image metadata"""
    instruments = [
        item
        for item in get_reference_catalog().get("instruments", [])
        if item.get("brand") == brand_id
    ]
    sorted_instruments = sorted(instruments, key=lambda i: i.get("model", "").lower())
    # Return basic info + image metadata
    return [
        {
            "id": i["id"],
            "model": i["model"],
            "year": i.get("year"),
            "description": i.get("description"),
            "imagen_url": i.get("imagen_url"),
            "image": i.get("image", {"url": None, "status": "pending"}),
            "valor_estimado": i.get("valor_estimado")
        }
        for i in sorted_instruments
    ]
