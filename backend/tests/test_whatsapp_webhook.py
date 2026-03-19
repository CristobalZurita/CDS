"""
test_whatsapp_webhook.py
========================
Tests para los endpoints de WhatsApp Webhook:
  GET  /api/v1/webhooks/whatsapp  — verificación Meta (hub.challenge)
  POST /api/v1/webhooks/whatsapp  — recepción de mensajes/status

No requiere SDK externo ni conexión a Meta — solo TestClient.
ADITIVO: no modifica tests existentes.
"""

import importlib
import app.main as _main
from fastapi.testclient import TestClient


def _make_client():
    importlib.reload(_main)
    return TestClient(_main.app)


# ── GET: verificación de webhook ──────────────────────────────────────────────

def test_verify_wrong_token():
    """Token incorrecto → 403 Forbidden."""
    client = _make_client()
    res = client.get(
        "/api/v1/webhooks/whatsapp",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "token-equivocado",
            "hub.challenge": "12345",
        },
    )
    assert res.status_code == 403


def test_verify_missing_params():
    """Sin parámetros de verificación → 403."""
    client = _make_client()
    res = client.get("/api/v1/webhooks/whatsapp")
    assert res.status_code == 403


def test_verify_wrong_mode():
    """hub.mode distinto a 'subscribe' → 403."""
    client = _make_client()
    res = client.get(
        "/api/v1/webhooks/whatsapp",
        params={
            "hub.mode": "unsubscribe",
            "hub.verify_token": "cualquiera",
            "hub.challenge": "abc",
        },
    )
    assert res.status_code == 403


def test_verify_correct_token(monkeypatch):
    """Token correcto → responde con hub.challenge exacto."""
    import app.routers.whatsapp_webhook as wh_mod
    monkeypatch.setattr(wh_mod.settings, "whatsapp_webhook_verify_token", "mi-token-secreto")

    client = _make_client()
    res = client.get(
        "/api/v1/webhooks/whatsapp",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "mi-token-secreto",
            "hub.challenge": "reto_12345",
        },
    )
    assert res.status_code == 200
    assert res.text == "reto_12345"


def test_verify_no_configured_token():
    """Sin WHATSAPP_WEBHOOK_VERIFY_TOKEN configurado → 403 aunque el token coincida vacío."""
    import app.routers.whatsapp_webhook as wh_mod

    original = wh_mod.settings.whatsapp_webhook_verify_token
    wh_mod.settings.whatsapp_webhook_verify_token = None
    try:
        client = _make_client()
        res = client.get(
            "/api/v1/webhooks/whatsapp",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": "",
                "hub.challenge": "abc",
            },
        )
        assert res.status_code == 403
    finally:
        wh_mod.settings.whatsapp_webhook_verify_token = original


# ── POST: recepción de eventos ────────────────────────────────────────────────

def test_receive_text_message():
    """Mensaje de texto entrante → 200 {"ok": True}."""
    client = _make_client()
    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "id": "wamid.001",
                                    "from": "56912345678",
                                    "type": "text",
                                    "text": {"body": "Hola, ¿tienen repuestos?"},
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    res = client.post("/api/v1/webhooks/whatsapp", json=payload)
    assert res.status_code == 200
    assert res.json() == {"ok": True}


def test_receive_text_message_triggers_autoreply(monkeypatch):
    import app.routers.whatsapp_webhook as wh_mod

    sent = {}

    def fake_send_session_text(*, to_phone, message):
        sent["to_phone"] = to_phone
        sent["message"] = message
        return True

    monkeypatch.setattr(
        wh_mod.WhatsAppService,
        "send_session_text",
        lambda self, to_phone, message: fake_send_session_text(to_phone=to_phone, message=message),
    )

    client = _make_client()
    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "id": "wamid.001",
                                    "from": "56912345678",
                                    "type": "text",
                                    "text": {"body": "Hola, cuanto sale?"},
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }

    res = client.post("/api/v1/webhooks/whatsapp", json=payload)

    assert res.status_code == 200
    assert res.json() == {"ok": True}
    assert sent["to_phone"] == "56912345678"
    assert "agendar revision" in sent["message"].lower()


def test_receive_status_update():
    """Actualización de estado de mensaje → 200 {"ok": True}."""
    client = _make_client()
    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "statuses": [
                                {
                                    "id": "wamid.001",
                                    "status": "delivered",
                                    "recipient_id": "56912345678",
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    res = client.post("/api/v1/webhooks/whatsapp", json=payload)
    assert res.status_code == 200
    assert res.json() == {"ok": True}


def test_receive_empty_entry():
    """Entry vacío → responde 200 sin crashear."""
    client = _make_client()
    res = client.post("/api/v1/webhooks/whatsapp", json={"entry": []})
    assert res.status_code == 200
    assert res.json() == {"ok": True}


def test_receive_media_message():
    """Mensaje de imagen → 200 {"ok": True}."""
    client = _make_client()
    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "id": "wamid.002",
                                    "from": "56987654321",
                                    "type": "image",
                                    "image": {"id": "media_id_abc"},
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    res = client.post("/api/v1/webhooks/whatsapp", json=payload)
    assert res.status_code == 200
    assert res.json() == {"ok": True}


def test_receive_malformed_body():
    """Body malformado (no JSON) → 422 o 400 — no debe crashear el servidor."""
    client = _make_client()
    res = client.post(
        "/api/v1/webhooks/whatsapp",
        content=b"no-es-json",
        headers={"Content-Type": "application/json"},
    )
    # FastAPI puede retornar 422 por validación o nuestro handler retorna {"ok": False}
    assert res.status_code in (200, 400, 422)
