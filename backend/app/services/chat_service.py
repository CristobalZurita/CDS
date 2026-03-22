"""
Orquesta la llamada a Gemini y detecta el marker de derivación [HANDOFF:X].
"""

import re

from app.core.gemini_client import send_chat
from app.core.chat_context import get_handoff_url

_HANDOFF_RE = re.compile(r"\[HANDOFF:(whatsapp|email)\]?", re.IGNORECASE)


def process_message(history: list[dict], message: str) -> dict:
    """
    Llama a Gemini con el historial y el mensaje del usuario.
    Extrae el marker [HANDOFF:X] si está presente.

    Retorna:
        {
            "reply": str,
            "handoff": "whatsapp" | "email" | None,
            "handoff_url": str | None,
        }
    """
    raw = send_chat(history, message)

    handoff = None
    match = _HANDOFF_RE.search(raw)
    if match:
        handoff = match.group(1).lower()
        raw = _HANDOFF_RE.sub("", raw).strip()

    return {
        "reply": raw,
        "handoff": handoff,
        "handoff_url": get_handoff_url(handoff) if handoff else None,
    }
