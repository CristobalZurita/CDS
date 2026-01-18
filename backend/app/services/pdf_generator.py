"""PDF generator placeholder."""
from typing import Dict, Any


def generate_pdf_placeholder(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status": "pending",
        "message": "PDF generation not implemented",
        "data": data,
    }
