"""
Placeholder module for future image analysis logic.
This module is intentionally minimal: it defines a stable import point
for later implementations (CV, ML, RAG integration).

Requirements:
- No heavy CV/ML imports
- No DB writes
- Pure placeholder functions that return neutral results
"""
from typing import Dict, Any


def analyze_image_placeholder(image_url: str) -> Dict[str, Any]:
    """
    Placeholder analysis function.

    Parameters
    - image_url: URL or path to image (string)

    Returns (example):
    {
        "status": "pending",  # or 'analyzed'
        "summary": "placeholder",
        "detected": {}
    }

    This function must remain dependency-free (no OpenCV, etc.)
    and act only as the formal entry point for future code.
    """
    # No processing here — just report that it's a stub
    return {
        "status": "pending",
        "summary": "no-analysis-performed",
        "detected": {}
    }
