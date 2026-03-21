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
import json
import time
import app.main as _main
from fastapi.testclient import TestClient
from app.models.payment import Payment, PaymentStatus
from app.models.purchase_request import PurchaseRequest, PurchaseRequestItem


def _make_client():
    importlib.reload(_main)
    return TestClient(_main.app)


def _create_purchase_request_with_payment(db):
    request = PurchaseRequest(
        status="pending_payment",
        notes="Solicitud creada desde tienda web | Despacho: Retiro en taller | Canal: pickup",
    )
    db.add(request)
    db.commit()
    db.refresh(request)

    db.add(
        PurchaseRequestItem(
            request_id=request.id,
            sku="GATEWAY-SKU-001",
            name="Gateway item",
            quantity=2,
            unit_price=3500,
            status="suggested",
        )
    )
    db.commit()

    payment = Payment(
        amount=7000,
        payment_method="transfer",
        transaction_id=f"REQ-{request.id}-{int(time.time() * 1000)}",
        status=PaymentStatus.PENDING,
        currency="CLP",
        payment_processor="manual",
        purchase_request_id=request.id,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    db.refresh(request)
    return request, payment


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


def test_initiate_purchase_request_payment_freezes_checkout_contract(test_client, admin_token, db):
    """Un pago ligado a purchase_request debe congelar snapshot y metadata de checkout."""
    import app.routers.payment_gateway as gw_mod

    request, payment = _create_purchase_request_with_payment(db)

    original_gateway = gw_mod.settings.payment_gateway
    original_token = gw_mod.settings.mercadopago_access_token
    original_initiate = gw_mod.PaymentGatewayService.initiate

    def _fake_initiate(self, amount, buy_order, title, return_url, notification_url=None):
        assert amount == 7000
        assert buy_order == payment.transaction_id
        assert return_url == "http://localhost/retorno"
        return {
            "preference_id": "pref-test-001",
            "init_point": "https://mp.example/checkout",
            "buy_order": buy_order,
            "processor": "mercadopago",
        }

    gw_mod.settings.payment_gateway = "mercadopago"
    gw_mod.settings.mercadopago_access_token = "test-token"
    gw_mod.PaymentGatewayService.initiate = _fake_initiate
    try:
        res = test_client.post(
            "/api/v1/payment-gateway/initiate",
            json={
                "payment_id": payment.id,
                "return_url": "http://localhost/retorno",
                "notification_url": "http://localhost/ipn",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert res.status_code == 200
        assert res.json()["gateway"] == "mercadopago"

        db.refresh(payment)
        db.refresh(request)
        assert payment.payment_method == "mercadopago"
        assert payment.payment_processor == "mercadopago"

        notes = json.loads(payment.notes or "{}")
        checkout = notes.get("checkout") or {}
        snapshot = checkout.get("request_snapshot") or {}
        shipping = snapshot.get("shipping") or {}
        assert checkout.get("version") == "purchase_request_checkout_v1"
        assert checkout.get("kind") == "gateway_session"
        assert checkout.get("provider") == "mercadopago"
        assert checkout.get("provider_status") == "initiated"
        assert checkout.get("origin_channel") == "admin_payment_gateway"
        assert checkout.get("gateway_external_id") == "pref-test-001"
        assert snapshot.get("request_id") == request.id
        assert snapshot.get("requested_amount") == 7000
        assert snapshot.get("total_items_amount") == 7000.0
        assert len(snapshot.get("items") or []) == 1
        assert shipping.get("shipping_label") == "Retiro en taller"
        assert shipping.get("shipping_channel") == "pickup"
    finally:
        gw_mod.settings.payment_gateway = original_gateway
        gw_mod.settings.mercadopago_access_token = original_token
        gw_mod.PaymentGatewayService.initiate = original_initiate


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


def test_mercadopago_ipn_updates_checkout_metadata(test_client, db):
    """El webhook debe persistir provider_status y payload bruto del intento."""
    import app.routers.payment_gateway as gw_mod

    _, payment = _create_purchase_request_with_payment(db)
    payment.payment_method = "mercadopago"
    payment.payment_processor = "mercadopago"
    payment.notes = json.dumps(
        {
            "checkout": {
                "version": "purchase_request_checkout_v1",
                "provider": "mercadopago",
                "provider_status": "initiated",
            }
        },
        ensure_ascii=False,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    original_lookup = gw_mod.PaymentGatewayService.get_mercadopago_payment

    def _fake_lookup(self, payment_id):
        assert payment_id == "mp-checkout-123"
        return {
            "id": payment_id,
            "status": "approved",
            "external_reference": payment.transaction_id,
        }

    gw_mod.PaymentGatewayService.get_mercadopago_payment = _fake_lookup
    try:
        res = test_client.post(
            "/api/v1/payment-gateway/mercadopago/ipn",
            json={"type": "payment", "data": {"id": "mp-checkout-123"}},
        )
        assert res.status_code == 200
        db.refresh(payment)
        notes = json.loads(payment.notes or "{}")
        checkout = notes.get("checkout") or {}
        assert checkout.get("provider_status") == "approved"
        assert (checkout.get("provider_payload") or {}).get("id") == "mp-checkout-123"
        assert payment.payment_date is not None
    finally:
        gw_mod.PaymentGatewayService.get_mercadopago_payment = original_lookup


def test_mercadopago_ipn_marks_purchase_request_paid_client(test_client, db):
    """Un pago gateway aprobado debe cerrar el request en paid_client."""
    import app.routers.payment_gateway as gw_mod

    request, payment = _create_purchase_request_with_payment(db)
    payment.payment_method = "mercadopago"
    payment.payment_processor = "mercadopago"
    db.add(payment)
    db.commit()
    db.refresh(payment)
    db.refresh(request)

    original_lookup = gw_mod.PaymentGatewayService.get_mercadopago_payment

    def _fake_lookup(self, payment_id):
        assert payment_id == "mp-request-paid-001"
        return {
            "id": payment_id,
            "status": "approved",
            "external_reference": payment.transaction_id,
        }

    gw_mod.PaymentGatewayService.get_mercadopago_payment = _fake_lookup
    try:
        res = test_client.post(
            "/api/v1/payment-gateway/mercadopago/ipn",
            json={"type": "payment", "data": {"id": "mp-request-paid-001"}},
        )
        assert res.status_code == 200
        db.refresh(payment)
        db.refresh(request)
        assert payment.status == PaymentStatus.SUCCESS
        assert request.status == "paid_client"
        assert "Pago confirmado por mercadopago" in str(request.notes or "")
    finally:
        gw_mod.PaymentGatewayService.get_mercadopago_payment = original_lookup


def test_mercadopago_ipn_keeps_purchase_request_pending_on_failure(test_client, db):
    """Un rechazo gateway no debe cerrar el request; debe dejarlo reintentable."""
    import app.routers.payment_gateway as gw_mod

    request, payment = _create_purchase_request_with_payment(db)
    payment.payment_method = "mercadopago"
    payment.payment_processor = "mercadopago"
    db.add(payment)
    db.commit()
    db.refresh(payment)
    db.refresh(request)

    original_lookup = gw_mod.PaymentGatewayService.get_mercadopago_payment

    def _fake_lookup(self, payment_id):
        assert payment_id == "mp-request-failed-001"
        return {
            "id": payment_id,
            "status": "rejected",
            "external_reference": payment.transaction_id,
        }

    gw_mod.PaymentGatewayService.get_mercadopago_payment = _fake_lookup
    try:
        res = test_client.post(
            "/api/v1/payment-gateway/mercadopago/ipn",
            json={"type": "payment", "data": {"id": "mp-request-failed-001"}},
        )
        assert res.status_code == 200
        db.refresh(payment)
        db.refresh(request)
        assert payment.status == PaymentStatus.FAILED
        assert request.status == "pending_payment"
        assert "Intento de pago mercadopago fallido" in str(request.notes or "")
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
