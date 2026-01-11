from fastapi import APIRouter
from typing import List
import json
from pathlib import Path

router = APIRouter(prefix="/brands", tags=["brands"])

DATA_PATH = Path(__file__).resolve().parents[5] / "src" / "assets" / "data"

@router.get("/", response_model=List[dict])
async def list_brands():
    """Return list of brands sorted A-Z by name"""
    with open(DATA_PATH / "brands.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    brands = data.get("brands", [])
    sorted_brands = sorted(brands, key=lambda b: b.get("name", "").lower())
    # Return minimal fields
    return [{"id": b["id"], "name": b["name"], "tier": b.get("tier")} for b in sorted_brands]

@router.get("/{brand_id}/models", response_model=List[dict])
async def list_models_by_brand(brand_id: str):
    """Return instruments for a given brand with image metadata"""
    with open(DATA_PATH / "instruments.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    instruments = [i for i in data.get("instruments", []) if i.get("brand") == brand_id]
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
