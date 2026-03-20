from datetime import datetime, timedelta

from app.core.timezone import CL_TZ, to_utc
from app.models.appointment import Appointment


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _next_business_slot(*, day_offset: int, hour: int = 9, minute: int = 0):
    local_value = datetime.now(CL_TZ).replace(second=0, microsecond=0)
    target = (local_value + timedelta(days=day_offset)).replace(hour=hour, minute=minute)
    while target.weekday() >= 5:
        target += timedelta(days=1)
    return to_utc(target)


class _FakeCalendarService:
    def __init__(self):
        self.updated = []
        self.deleted = []

    def update_event(self, **kwargs):
        self.updated.append(kwargs)
        return True

    def delete_event(self, **kwargs):
        self.deleted.append(kwargs)
        return True


def test_rescheduling_appointment_updates_google_event(monkeypatch, db, test_client, admin_token):
    original_fecha = _next_business_slot(day_offset=1, hour=9, minute=0)
    next_fecha = _next_business_slot(day_offset=2, hour=10, minute=30)

    appointment = Appointment(
        nombre="Cliente Agenda",
        email="agenda@example.com",
        telefono="+56912345678",
        fecha=original_fecha,
        fecha_fin=original_fecha + timedelta(minutes=30),
        estado="confirmado",
        google_calendar_id="gcal-update-123",
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    fake_service = _FakeCalendarService()
    monkeypatch.setattr("app.routers.appointment.get_calendar_service", lambda: fake_service)

    response = test_client.patch(
        f"/api/v1/appointments/{appointment.id}",
        headers=_auth_headers(admin_token),
        json={
            "fecha": next_fecha.isoformat(),
            "mensaje": "Reprogramada por disponibilidad",
        },
    )

    assert response.status_code == 200, response.text

    db.refresh(appointment)
    assert appointment.fecha == next_fecha.replace(tzinfo=None)
    assert appointment.original_fecha == original_fecha.replace(tzinfo=None)
    assert appointment.reschedule_count == 1
    assert fake_service.updated
    assert fake_service.updated[0]["event_id"] == "gcal-update-123"
    assert fake_service.updated[0]["start_time"] == next_fecha.replace(tzinfo=None)


def test_cancelling_appointment_deletes_google_event(monkeypatch, db, test_client, admin_token):
    fecha = _next_business_slot(day_offset=1, hour=11, minute=0)

    appointment = Appointment(
        nombre="Cliente Cancelacion",
        email="cancel@example.com",
        telefono="+56912345679",
        fecha=fecha,
        fecha_fin=fecha + timedelta(minutes=30),
        estado="confirmado",
        google_calendar_id="gcal-delete-123",
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    fake_service = _FakeCalendarService()
    monkeypatch.setattr("app.routers.appointment.get_calendar_service", lambda: fake_service)

    response = test_client.patch(
        f"/api/v1/appointments/{appointment.id}",
        headers=_auth_headers(admin_token),
        json={
            "estado": "cancelado",
            "cancellation_reason": "Cliente reprogramara mas adelante",
        },
    )

    assert response.status_code == 200, response.text

    db.refresh(appointment)
    assert appointment.estado == "cancelado"
    assert appointment.cancelled_at is not None
    assert fake_service.deleted
    assert fake_service.deleted[0]["event_id"] == "gcal-delete-123"
