"""
Payment Gateway Service
========================
Abstraction layer over Transbank Webpay Plus and MercadoPago Checkout Pro.
Uses the existing Payment model (fields: payment_method, payment_processor,
transaction_id, currency, amount, status already exist).

Configured via environment variables (see config.py):
  PAYMENT_GATEWAY=transbank  |  mercadopago
  TRANSBANK_COMMERCE_CODE, TRANSBANK_API_KEY, TRANSBANK_ENVIRONMENT
  MERCADOPAGO_ACCESS_TOKEN

ADITIVO: nuevo servicio, no modifica existentes.
"""

import logging
import uuid
from typing import Any, Dict, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


# ── Transbank Webpay Plus ─────────────────────────────────────────────────────

def _require_transbank_credentials() -> tuple[str, str]:
    """Require explicit Transbank credentials for both integration and production."""
    commerce_code = (settings.transbank_commerce_code or "").strip()
    api_key = (settings.transbank_api_key or "").strip()
    if commerce_code and api_key:
        return commerce_code, api_key
    raise RuntimeError(
        "TRANSBANK_COMMERCE_CODE and TRANSBANK_API_KEY must be configured in .env "
        "for the selected Transbank environment."
    )


def _transbank_create(
    amount: int,
    buy_order: str,
    session_id: str,
    return_url: str,
) -> Dict[str, Any]:
    """
    Initiate a Transbank Webpay Plus transaction.
    Returns {"token": ..., "url": ..., "buy_order": ...}
    """
    try:
        from transbank.webpay.webpay_plus.transaction import Transaction  # type: ignore
        from transbank.common.options import WebpayOptions  # type: ignore
        from transbank.common.integration_type import IntegrationType  # type: ignore
    except ImportError:
        raise RuntimeError(
            "transbank-sdk not installed. Run: pip install transbank-sdk"
        )

    commerce_code, api_key = _require_transbank_credentials()
    if settings.transbank_environment == "production":
        options = WebpayOptions(
            commerce_code=commerce_code,
            api_key=api_key,
            integration_type=IntegrationType.LIVE,
        )
    else:
        options = WebpayOptions(
            commerce_code=commerce_code,
            api_key=api_key,
            integration_type=IntegrationType.TEST,
        )

    tx = Transaction(options)
    response = tx.create(
        buy_order=buy_order,
        session_id=session_id,
        amount=amount,
        return_url=return_url,
    )
    return {
        "token": response.token,
        "url": response.url,
        "buy_order": buy_order,
        "processor": "transbank",
    }


def _transbank_commit(token: str) -> Dict[str, Any]:
    """Confirm/commit a Webpay Plus transaction after redirect."""
    try:
        from transbank.webpay.webpay_plus.transaction import Transaction  # type: ignore
        from transbank.common.options import WebpayOptions  # type: ignore
        from transbank.common.integration_type import IntegrationType  # type: ignore
    except ImportError:
        raise RuntimeError("transbank-sdk not installed.")

    commerce_code, api_key = _require_transbank_credentials()
    if settings.transbank_environment == "production":
        options = WebpayOptions(
            commerce_code=commerce_code,
            api_key=api_key,
            integration_type=IntegrationType.LIVE,
        )
    else:
        options = WebpayOptions(
            commerce_code=commerce_code,
            api_key=api_key,
            integration_type=IntegrationType.TEST,
        )

    tx = Transaction(options)
    response = tx.commit(token=token)
    return {
        "authorization_code": response.authorization_code,
        "response_code": response.response_code,
        "amount": response.amount,
        "buy_order": response.buy_order,
        "status": response.status,
        "vci": getattr(response, "vci", None),
        "processor": "transbank",
    }


# ── MercadoPago Checkout Pro ──────────────────────────────────────────────────

def _mercadopago_create(
    amount: int,
    title: str,
    buy_order: str,
    back_urls: Dict[str, str],
    notification_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a MercadoPago preference (Checkout Pro).
    Returns {"preference_id": ..., "init_point": ..., "sandbox_init_point": ...}
    """
    try:
        import mercadopago  # type: ignore
    except ImportError:
        raise RuntimeError(
            "mercadopago not installed. Run: pip install mercadopago"
        )

    if not settings.mercadopago_access_token:
        raise RuntimeError("MERCADOPAGO_ACCESS_TOKEN not configured.")

    sdk = mercadopago.SDK(settings.mercadopago_access_token)

    preference_data: Dict[str, Any] = {
        "items": [
            {
                "id": buy_order,
                "title": title,
                "quantity": 1,
                "unit_price": float(amount),
                "currency_id": "CLP",
            }
        ],
        "external_reference": buy_order,
        "back_urls": back_urls,
        "auto_return": "approved",
    }
    if notification_url:
        preference_data["notification_url"] = notification_url

    response = sdk.preference().create(preference_data)
    pref = response.get("response", {})
    return {
        "preference_id": pref.get("id"),
        "init_point": pref.get("init_point"),
        "sandbox_init_point": pref.get("sandbox_init_point"),
        "buy_order": buy_order,
        "processor": "mercadopago",
    }


# ── Public facade ─────────────────────────────────────────────────────────────

class PaymentGatewayService:
    """
    Unified interface for payment gateway operations.
    Select gateway via PAYMENT_GATEWAY env var ("transbank" or "mercadopago").
    """

    def __init__(self):
        self.gateway = settings.payment_gateway.lower()

    @property
    def is_configured(self) -> bool:
        if self.gateway == "transbank":
            return bool(settings.transbank_commerce_code and settings.transbank_api_key)
        if self.gateway == "mercadopago":
            return bool(settings.mercadopago_access_token)
        return False

    def initiate(
        self,
        amount: int,
        buy_order: str,
        title: str,
        return_url: str,
        notification_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Start a payment transaction.
        Returns gateway-specific payload the frontend needs to redirect the user.
        """
        if not self.is_configured:
            raise RuntimeError(
                f"Payment gateway '{self.gateway}' is not configured. "
                "Set PAYMENT_GATEWAY, TRANSBANK_* or MERCADOPAGO_* in .env"
            )

        session_id = str(uuid.uuid4())

        if self.gateway == "transbank":
            return _transbank_create(
                amount=amount,
                buy_order=buy_order,
                session_id=session_id,
                return_url=return_url,
            )

        if self.gateway == "mercadopago":
            back_urls = {
                "success": return_url,
                "pending": return_url,
                "failure": return_url,
            }
            return _mercadopago_create(
                amount=amount,
                title=title,
                buy_order=buy_order,
                back_urls=back_urls,
                notification_url=notification_url,
            )

        raise RuntimeError(f"Unknown payment gateway: '{self.gateway}'")

    def commit(self, token: str) -> Dict[str, Any]:
        """Confirm a Transbank transaction after redirect."""
        if self.gateway != "transbank":
            raise RuntimeError("commit() is only for Transbank gateway.")
        return _transbank_commit(token)
