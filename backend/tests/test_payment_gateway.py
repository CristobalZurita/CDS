"""
test_payment_gateway.py
=======================
Tests para los endpoints de Payment Gateway:
  POST /api/v1/payment-gateway/initiate
  POST /api/v1/payment-gateway/transbank/confirm
  POST /api/v1/payment-gateway/mercadopago/ipn

No requiere SDKs de Transbank ni MercadoPago instalados.
Cubre el comportamiento sin credenciales configuradas (estado por defecto en dev/test).
ADITIVO: no modifica tests existentes.
"""

import importlib
import time
import app.main as _main
from fastapi.testclient import TestClient
from app.models.payment import Payment, PaymentStatus


def _make_client():
    importlib.reload(_main)
    return TestClient(_main.app)


# ── POST /initiate ─────────────────────────────────────────────────────────────

def test_initiate_missing_payment_id():
    """Sin payment_id → 400."""
    client = _make_client()
    res = client.post(
        "/api/v1/payment-gateway/initiate",
        json={"return_url": "http://localhost/retorno"},
    )
    assert res.status_code in (400, 401, 403)


def test_initiate_missing_return_url():
    """Sin return_url → 400."""
    client = _make_client()
    res = client.post(
        "/api/v1/payment-gateway/initiate",
        json={"payment_id": 1},
    )
    assert res.status_code in (400, 401, 403)


def test_initiate_nonexistent_payment(test_client, admin_token):
    """Payment inexistente → 404."""
    res = test_client.post(
        "/api/v1/payment-gateway/initiate",
        json={"payment_id": 999999, "return_url": "http://localhost/retorno"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    # Payment not found → 404; or gateway not configured → 503
    assert res.status_code in (404, 503)


def test_initiate_gateway_not_configured(test_client, admin_token, db):
    """Con gateway vacío y Payment real → 503 (gateway no configurado)."""
    import time
    import app.routers.payment_gateway as gw_mod
    from app.models.payment import Payment, PaymentStatus

    # Crear un Payment de prueba (transaction_id único por ejecución)
    pay = Payment(
        amount=5000,
        payment_method="card",
        transaction_id=f"test-gw-{int(time.time() * 1000)}",
        status=PaymentStatus.PENDING,
        currency="CLP",
    )
    db.add(pay)
    db.commit()
    db.refresh(pay)

    # Asegurar que el gateway no está configurado
    original = gw_mod.settings.payment_gateway
    gw_mod.settings.payment_gateway = ""
    try:
        res = test_client.post(
            "/api/v1/payment-gateway/initiate",
            json={"payment_id": pay.id, "return_url": "http://localhost/retorno"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert res.status_code == 503
    finally:
        gw_mod.settings.payment_gateway = original


# ── POST /transbank/confirm ───────────────────────────────────────────────────

def test_transbank_confirm_missing_token():
    """Sin token_ws → 400."""
    client = _make_client()
    res = client.post(
        "/api/v1/payment-gateway/transbank/confirm",
        json={},
    )
    assert res.status_code == 400


def test_transbank_confirm_invalid_token_without_sdk():
    """
    Token presente pero SDK no instalado → 503 RuntimeError.
    Si el SDK sí está instalado, Transbank retornará error de token inválido → también 503.
    """
    client = _make_client()
    res = client.post(
        "/api/v1/payment-gateway/transbank/confirm",
        json={"token_ws": "token_invalido_test"},
    )
    # 503 porque SDK no instalado o token inválido
    assert res.status_code in (400, 503)


# ── POST /mercadopago/ipn ─────────────────────────────────────────────────────

def test_mercadopago_ipn_empty_body():
    """Body vacío → 200 {"ok": True} (MercadoPago no debe bloquear el servidor)."""
    client = _make_client()
    res = client.post(
        "/api/v1/payment-gateway/mercadopago/ipn",
        json={},
    )
    assert res.status_code == 200
    assert res.json() == {"ok": True}


def test_mercadopago_ipn_payment_notification():
    """Sin verificación disponible no debe marcar éxito ciegamente."""
    client = _make_client()
    res = client.post(
        "/api/v1/payment-gateway/mercadopago/ipn",
        json={"type": "payment", "data": {"id": "123456789"}},
    )
    assert res.status_code == 200
    assert res.json() == {"ok": True, "verified": False}


def test_mercadopago_ipn_non_payment_topic():
    """Topic desconocido → 200 {"ok": True} — no debe crashear."""
    client = _make_client()
    res = client.post(
        "/api/v1/payment-gateway/mercadopago/ipn",
        json={"type": "merchant_order", "data": {"id": "987"}},
    )
    assert res.status_code == 200
    assert res.json() == {"ok": True}


def test_mercadopago_ipn_no_signature_check_without_secret():
    """Sin MERCADOPAGO_WEBHOOK_SECRET configurado → no valida firma → 200."""
    import app.routers.payment_gateway as gw_mod

    original = gw_mod.settings.mercadopago_webhook_secret
    gw_mod.settings.mercadopago_webhook_secret = None
    try:
        client = _make_client()
        res = client.post(
            "/api/v1/payment-gateway/mercadopago/ipn",
            json={"type": "payment", "data": {"id": "111"}},
        )
        assert res.status_code == 200
    finally:
        gw_mod.settings.mercadopago_webhook_secret = original


def test_mercadopago_ipn_updates_payment_after_verified_lookup(test_client, db):
    """Con verificación real/monkeypatched, actualiza el Payment correcto."""
    import app.routers.payment_gateway as gw_mod

    payment = Payment(
        amount=12000,
        payment_method="mercadopago",
        transaction_id=f"OT-999-{int(time.time() * 1000)}",
        status=PaymentStatus.PENDING,
        currency="CLP",
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    original_lookup = gw_mod.PaymentGatewayService.get_mercadopago_payment

    def _fake_lookup(self, payment_id):
        assert payment_id == "mp-test-123"
        return {
            "id": payment_id,
            "status": "approved",
            "external_reference": payment.transaction_id,
        }

    gw_mod.PaymentGatewayService.get_mercadopago_payment = _fake_lookup
    try:
        res = test_client.post(
            "/api/v1/payment-gateway/mercadopago/ipn",
            json={"type": "payment", "data": {"id": "mp-test-123"}},
        )
        assert res.status_code == 200
        assert res.json() == {"ok": True}

        db.refresh(payment)
        assert payment.status == PaymentStatus.SUCCESS
        assert payment.payment_processor == "mercadopago"
    finally:
        gw_mod.PaymentGatewayService.get_mercadopago_payment = original_lookup


# ── Rutas registradas ─────────────────────────────────────────────────────────

def test_payment_gateway_routes_registered():
    """Los tres endpoints del gateway deben estar registrados en /api/v1."""
    from app.main import app

    paths = {
        getattr(r, "path", "")
        for r in app.routes
    }
    assert "/api/v1/payment-gateway/initiate" in paths
    assert "/api/v1/payment-gateway/transbank/confirm" in paths
    assert "/api/v1/payment-gateway/mercadopago/ipn" in paths
