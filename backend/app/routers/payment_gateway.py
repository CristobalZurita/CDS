"""
Payment Gateway Router
======================
Endpoints for initiating and confirming payments via
Transbank Webpay Plus or MercadoPago Checkout Pro.

Uses the existing Payment model (transaction_id, payment_processor,
payment_method, currency, status, amount — all fields already in the model).

Routes:
  POST /payment-gateway/initiate          — create transaction, get redirect URL
  POST /payment-gateway/transbank/confirm — commit Transbank token after redirect
  POST /payment-gateway/mercadopago/ipn   — MercadoPago IPN webhook (no auth)

ADITIVO: nuevo router, no modifica existentes.
"""

import logging
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import require_permission
from app.models.payment import Payment, PaymentStatus
from app.services.payment_gateway_service import PaymentGatewayService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payment-gateway", tags=["Payment Gateway"])


# ── Initiate payment ──────────────────────────────────────────────────────────

@router.post("/initiate")
def initiate_payment(
    payload: Dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("payments", "create")),
):
    """
    Start a payment transaction.

    Body:
      payment_id   int   — existing Payment row to associate
      return_url   str   — URL the gateway redirects to after payment
      notification_url  str (optional) — webhook URL for MercadoPago IPN

    Returns gateway-specific redirect data:
    - Transbank: { token, url }          → POST form to url with token
    - MercadoPago: { init_point }        → redirect user to init_point
    """
    payment_id = payload.get("payment_id")
    return_url = payload.get("return_url", "")
    notification_url = payload.get("notification_url")

    if not payment_id:
        raise HTTPException(status_code=400, detail="payment_id es requerido")
    if not return_url:
        raise HTTPException(status_code=400, detail="return_url es requerido")

    payment = db.query(Payment).filter(Payment.id == int(payment_id)).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    if not payment.amount or payment.amount <= 0:
        raise HTTPException(status_code=400, detail="El pago no tiene monto válido")

    svc = PaymentGatewayService()
    if not svc.is_configured:
        raise HTTPException(
            status_code=503,
            detail="Pasarela de pago no configurada. Contacte al administrador.",
        )

    buy_order = payment.transaction_id or f"OT-{payment.repair_id or payment.id}"
    title = f"Pago OT #{payment.repair_id or payment.id}"

    try:
        result = svc.initiate(
            amount=int(payment.amount),
            buy_order=buy_order,
            title=title,
            return_url=return_url,
            notification_url=notification_url,
        )
    except RuntimeError as exc:
        logger.error("payment_gateway.initiate error: %s", exc)
        raise HTTPException(status_code=503, detail=str(exc))

    # Update payment record with processor info
    payment.payment_processor = result.get("processor", svc.gateway)
    payment.payment_method = svc.gateway
    if not payment.transaction_id:
        payment.transaction_id = buy_order
    if not payment.currency:
        payment.currency = "CLP"
    db.commit()

    return {"ok": True, "gateway": svc.gateway, **result}


# ── Transbank: commit after redirect ─────────────────────────────────────────

@router.post("/transbank/confirm")
def transbank_confirm(
    payload: Dict,
    db: Session = Depends(get_db),
):
    """
    Called after Transbank redirects back to return_url.
    Frontend passes token_ws (from query param) to confirm the transaction.

    Body: { token_ws: str }
    No auth required — Transbank handles security via one-time token.
    """
    token = payload.get("token_ws") or payload.get("token")
    if not token:
        raise HTTPException(status_code=400, detail="token_ws es requerido")

    svc = PaymentGatewayService()
    try:
        result = svc.commit(token)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    # response_code 0 = approved in Transbank
    approved = result.get("response_code") == 0

    # Locate payment by buy_order / transaction_id
    buy_order = result.get("buy_order")
    payment = None
    if buy_order:
        payment = (
            db.query(Payment)
            .filter(Payment.transaction_id == buy_order)
            .order_by(Payment.id.desc())
            .first()
        )

    if payment:
        payment.status = PaymentStatus.SUCCESS if approved else PaymentStatus.FAILED
        payment.payment_processor = "transbank"
        db.commit()

    return {
        "ok": approved,
        "approved": approved,
        "payment_id": payment.id if payment else None,
        **result,
    }


# ── MercadoPago: IPN webhook ──────────────────────────────────────────────────

@router.post("/mercadopago/ipn")
async def mercadopago_ipn(request: Request, db: Session = Depends(get_db)):
    """
    MercadoPago IPN / webhook notification.
    No auth — MercadoPago posts here on payment status changes.

    Verifies signature via MERCADOPAGO_WEBHOOK_SECRET if configured,
    then updates the corresponding Payment row.
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Basic signature verification
    if settings.mercadopago_webhook_secret:
        sig_header = request.headers.get("x-signature", "")
        data_id = request.query_params.get("data.id") or body.get("data", {}).get("id", "")
        ts = ""
        sig = ""
        for part in sig_header.split(","):
            k, _, v = part.partition("=")
            if k.strip() == "ts":
                ts = v.strip()
            elif k.strip() == "v1":
                sig = v.strip()

        if ts and sig and data_id:
            import hashlib
            import hmac
            manifest = f"id:{data_id};request-id:{request.headers.get('x-request-id', '')};ts:{ts};"
            expected = hmac.new(
                settings.mercadopago_webhook_secret.encode(),
                manifest.encode(),
                hashlib.sha256,
            ).hexdigest()
            if not hmac.compare_digest(expected, sig):
                logger.warning("MercadoPago IPN: invalid signature")
                raise HTTPException(status_code=403, detail="Invalid signature")

    # Process payment notification
    topic = body.get("type") or request.query_params.get("topic")
    resource_id = str(
        (body.get("data") or {}).get("id")
        or request.query_params.get("id")
        or ""
    )

    if topic == "payment" and resource_id:
        logger.info("MercadoPago IPN: payment notification id=%s", resource_id)
        svc = PaymentGatewayService()
        try:
            provider_payment = svc.get_mercadopago_payment(resource_id)
        except RuntimeError as exc:
            logger.warning("MercadoPago IPN: verification skipped for id=%s (%s)", resource_id, exc)
            return {"ok": True, "verified": False}

        provider_status = str(provider_payment.get("status") or "").strip().lower()
        external_reference = str(provider_payment.get("external_reference") or "").strip()
        payment = None
        if external_reference:
            payment = (
                db.query(Payment)
                .filter(Payment.transaction_id == external_reference)
                .order_by(Payment.id.desc())
                .first()
            )

        if payment:
            if provider_status == "approved":
                payment.status = PaymentStatus.SUCCESS
            elif provider_status in {"rejected", "cancelled", "refunded", "charged_back"}:
                payment.status = PaymentStatus.FAILED
            else:
                payment.status = PaymentStatus.PENDING
            payment.payment_processor = "mercadopago"
            db.commit()
            logger.info(
                "Payment %d updated via MercadoPago IPN (status=%s)",
                payment.id,
                provider_status or "unknown",
            )
        else:
            logger.warning(
                "MercadoPago IPN: no local payment found for external_reference=%s",
                external_reference or "<empty>",
            )
    else:
        logger.debug("MercadoPago IPN: unhandled topic=%s id=%s", topic, resource_id)

    return {"ok": True}
