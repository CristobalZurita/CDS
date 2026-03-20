from datetime import datetime

from app.core.config import settings
from app.services.email_service import EmailService, send_appointment_confirmation


def _capture_outbound_email(monkeypatch, service: EmailService) -> dict[str, str]:
    payload: dict[str, str] = {}

    def _fake_send_email(to_email: str, subject: str, html_content: str) -> bool:
        payload["to_email"] = to_email
        payload["subject"] = subject
        payload["html_content"] = html_content
        return True

    monkeypatch.setattr(service, "_send_email", _fake_send_email)
    return payload


def test_customer_email_templates_use_public_base_url(monkeypatch):
    monkeypatch.setattr(settings, "public_base_url", "https://tenant.example", raising=False)
    monkeypatch.setattr(settings, "from_email", "ops@tenant.example", raising=False)

    service = EmailService()
    payload = _capture_outbound_email(monkeypatch, service)

    ok = service.send_quotation_saved_email(
        email="cliente@example.com",
        customer_name="Cliente Demo",
        quotation_id="Q-001",
        instrument="Equipo Demo",
        min_price=1000,
        max_price=1500,
    )

    assert ok is True
    assert payload["to_email"] == "cliente@example.com"
    assert "https://tenant.example/cotizaciones/Q-001" in payload["html_content"]
    assert 'mailto:ops@tenant.example' in payload["html_content"]
    assert "cirujanodesintetizadores.cl/cotizaciones" not in payload["html_content"]


def test_reminder_and_pickup_emails_do_not_embed_hardcoded_whatsapp_links(monkeypatch):
    monkeypatch.setattr(settings, "public_base_url", "https://tenant.example", raising=False)
    monkeypatch.setattr(settings, "from_email", "ops@tenant.example", raising=False)

    service = EmailService()
    reminder_payload = _capture_outbound_email(monkeypatch, service)

    reminder_ok = service.send_appointment_reminder_email(
        email="cliente@example.com",
        customer_name="Cliente Demo",
        appointment_date="20/03/2026",
        appointment_time="10:30",
    )

    assert reminder_ok is True
    assert "wa.me/" not in reminder_payload["html_content"]
    assert 'mailto:ops@tenant.example?subject=Confirmacion%20de%20cita%2020/03/2026' in reminder_payload["html_content"]

    pickup_payload = _capture_outbound_email(monkeypatch, service)
    pickup_ok = service.send_ready_for_pickup_email(
        email="cliente@example.com",
        customer_name="Cliente Demo",
        repair_id="R-001",
        instrument="Equipo Demo",
        total_cost=25000,
    )

    assert pickup_ok is True
    assert "wa.me/" not in pickup_payload["html_content"]
    assert 'mailto:ops@tenant.example?subject=Coordinar%20retiro%20reparacion%20R-001' in pickup_payload["html_content"]


async def test_appointment_confirmation_uses_public_base_url(monkeypatch):
    monkeypatch.setattr(settings, "public_base_url", "https://tenant.example", raising=False)
    monkeypatch.setattr(settings, "from_email", "ops@tenant.example", raising=False)

    payload: dict[str, str] = {}

    def _fake_send_email(self, *, to_email: str, subject: str, html_content: str) -> bool:
        payload["to_email"] = to_email
        payload["subject"] = subject
        payload["html_content"] = html_content
        return True

    monkeypatch.setattr("app.services.email_service.EmailService.send_email", _fake_send_email)

    ok = await send_appointment_confirmation(
        email="cliente@example.com",
        nombre="Cliente Demo",
        fecha=datetime(2026, 3, 20, 10, 30),
        appointment_id=123,
    )

    assert ok is True
    assert payload["to_email"] == "cliente@example.com"
    assert "https://tenant.example" in payload["html_content"]
    assert "www.cirujanodesintetizadores.cl" not in payload["html_content"]
