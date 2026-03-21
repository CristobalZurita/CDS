from datetime import datetime, timedelta

from app.core.config import settings
from app.core.timezone import CL_TZ


def _next_valid_slot():
    target = datetime.now(CL_TZ) + timedelta(days=1)
    while target.weekday() >= 5:
        target += timedelta(days=1)
    return target.replace(hour=14, minute=30, second=0, microsecond=0)


def _appointment_payload():
    return {
        "nombre": "Prueba Csrf",
        "email": "csrf.test@example.com",
        "telefono": "+56912345678",
        "fecha": _next_valid_slot().isoformat(),
        "mensaje": "Prueba CSRF",
    }


def test_public_mutation_requires_csrf_when_enforced(test_client, monkeypatch):
    monkeypatch.setattr(settings, "enforce_csrf", True)

    response = test_client.post("/api/v1/appointments/", json=_appointment_payload())

    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid or missing CSRF token"


def test_public_mutation_accepts_valid_signed_csrf_token(test_client, monkeypatch):
    monkeypatch.setattr(settings, "enforce_csrf", True)

    token_response = test_client.get("/api/csrf-token")
    assert token_response.status_code == 200, token_response.text
    token = token_response.json()["token"]

    response = test_client.post(
        "/api/v1/appointments/",
        json=_appointment_payload(),
        headers={"X-CSRF-Token": token},
    )

    assert response.status_code == 201, response.text
    payload = response.json()
    assert payload["nombre"] == "Prueba Csrf"
    assert payload["email"] == "csrf.test@example.com"


def test_public_mutation_rejects_tampered_csrf_token(test_client, monkeypatch):
    monkeypatch.setattr(settings, "enforce_csrf", True)

    token_response = test_client.get("/api/csrf-token")
    assert token_response.status_code == 200, token_response.text
    token = token_response.json()["token"]
    tampered_token = f"{token[:-1]}{'A' if token[-1] != 'A' else 'B'}"

    response = test_client.post(
        "/api/v1/appointments/",
        json=_appointment_payload(),
        headers={"X-CSRF-Token": tampered_token},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid or missing CSRF token"
