"""
WhatsApp Webhook — Meta Cloud API
==================================
Handles two operations:
  GET  /webhooks/whatsapp  — Meta verification handshake (hub.challenge)
  POST /webhooks/whatsapp  — Receive incoming message events

Configure WHATSAPP_WEBHOOK_VERIFY_TOKEN in .env (must match what you set in
Meta Developer Console › Webhooks › Verify Token).

ADITIVO: nuevo router, no modifica existentes.
"""

import logging
from fastapi import APIRouter, Query, Request, Response

from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["WhatsApp Webhook"])


# ── Verification handshake ────────────────────────────────────────────────────

@router.get("/whatsapp")
def verify_whatsapp_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    """
    Meta Cloud API calls this endpoint to verify the webhook URL.
    Responds with hub.challenge if the verify token matches.
    """
    expected = settings.whatsapp_webhook_verify_token
    if (
        hub_mode == "subscribe"
        and hub_verify_token
        and expected
        and hub_verify_token == expected
        and hub_challenge
    ):
        return Response(content=hub_challenge, media_type="text/plain")

    logger.warning(
        "WhatsApp webhook verification failed: mode=%r token_match=%s",
        hub_mode,
        hub_verify_token == expected,
    )
    return Response(content="Forbidden", status_code=403, media_type="text/plain")


# ── Incoming event dispatcher ─────────────────────────────────────────────────

@router.post("/whatsapp")
async def receive_whatsapp_event(request: Request):
    """
    Receives incoming WhatsApp Cloud API events (messages, status updates).

    Current behaviour:
    - Logs every incoming text/media/status event.
    - Extension points for: auto-reply, OT linking, lead creation.

    Returns 200 immediately so Meta does not retry.
    """
    try:
        body = await request.json()
    except Exception:
        logger.error("WhatsApp webhook: could not parse JSON body")
        return {"ok": False}

    for entry in (body.get("entry") or []):
        for change in (entry.get("changes") or []):
            value = change.get("value") or {}
            # Incoming messages
            for message in (value.get("messages") or []):
                _handle_message(message, value)
            # Status updates (sent / delivered / read / failed)
            for status in (value.get("statuses") or []):
                _handle_status(status)

    return {"ok": True}


# ── Internal handlers ─────────────────────────────────────────────────────────

def _handle_message(message: dict, value: dict) -> None:
    """
    Process a single incoming message object.
    Extend here to:
    - Match phone to existing Client → attach note to open OT
    - Create Lead if no match
    - Trigger auto-reply via WhatsAppService.send_text()
    """
    msg_type = message.get("type", "unknown")
    from_phone = message.get("from", "")
    msg_id = message.get("id", "")

    if msg_type == "text":
        body_text = (message.get("text") or {}).get("body", "")
        logger.info(
            "WhatsApp inbound text | from=%s msg_id=%s body=%r",
            from_phone, msg_id, body_text,
        )
    elif msg_type in ("image", "audio", "video", "document", "sticker"):
        media_id = (message.get(msg_type) or {}).get("id", "")
        logger.info(
            "WhatsApp inbound %s | from=%s msg_id=%s media_id=%s",
            msg_type, from_phone, msg_id, media_id,
        )
    else:
        logger.info(
            "WhatsApp inbound %s | from=%s msg_id=%s",
            msg_type, from_phone, msg_id,
        )


def _handle_status(status: dict) -> None:
    """Log delivery / read receipts for outgoing messages."""
    msg_id = status.get("id", "")
    status_val = status.get("status", "")
    recipient = status.get("recipient_id", "")
    logger.debug(
        "WhatsApp status update | msg_id=%s status=%s recipient=%s",
        msg_id, status_val, recipient,
    )
