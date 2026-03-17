"""AI endpoints (API v1).

Fuera del flujo público canónico del cotizador.
"""
from fastapi import APIRouter, Request
from app.services.ai_detector import analyze_image
from app.core.ratelimit import limiter

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/analyze", summary="Análisis experimental de imagen", description="Endpoint aislado de IA. No participa del flujo público canónico del cotizador.")
@limiter.limit("10/minute")
def analyze(payload: dict, request: Request):
    image_url = payload.get("image_url") or payload.get("image") or ""
    return analyze_image(image_url)
