"""Lightweight AI detector placeholder."""
from typing import Dict, Any
from app.services.image_analysis import analyze_image_placeholder


def analyze_image(image_url: str) -> Dict[str, Any]:
    if not image_url:
        return {
            "status": "error",
            "message": "missing image_url",
            "detected": {}
        }
    return analyze_image_placeholder(image_url)
