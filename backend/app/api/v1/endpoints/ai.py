"""AI endpoints (API v1)."""
from fastapi import APIRouter
from app.services.ai_detector import analyze_image

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/analyze")
def analyze(payload: dict):
    image_url = payload.get("image_url") or payload.get("image") or ""
    return analyze_image(image_url)
