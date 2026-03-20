"""
Router for Appointment endpoints
Handles appointment booking and management
"""

import os
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from app.core.database import get_db, SessionLocal
from app.core.ratelimit import limiter
from app.core.dependencies import require_permission
from app.core.timezone import CL_TZ, to_local, to_utc
from app.crud.appointment import (
    create_appointment,
    get_appointment,
    get_appointments,
    get_appointments_by_email,
    get_appointments_by_date_range,
    update_appointment,
    delete_appointment,
    get_pending_appointments,
    get_confirmed_appointments
)
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse
)
from app.services.email_service import send_appointment_confirmation
try:
    from app.services.google_calendar_service import (
        get_calendar_service,
        sync_to_google_calendar,
    )
except Exception:
    get_calendar_service = None
    sync_to_google_calendar = None

router = APIRouter(prefix="/appointments", tags=["appointments"])


async def _bg_sync_calendar(appointment_id: int) -> None:
    """Sincroniza una cita con Google Calendar en background (sesión propia)."""
    if not sync_to_google_calendar:
        return
    db = SessionLocal()
    try:
        db_appointment = await get_appointment(db, appointment_id)
        if not db_appointment:
            return
        calendar_id = await sync_to_google_calendar(db_appointment)
        if calendar_id:
            await update_appointment(
                db,
                appointment_id,
                AppointmentUpdate(google_calendar_id=calendar_id),
            )
    except Exception as e:
        print(f"Error syncing to Google Calendar (background): {e}")
    finally:
        db.close()


def _appointment_end_time(appointment) -> datetime:
    if getattr(appointment, "fecha_fin", None):
        return appointment.fecha_fin
    duration_minutes = int(getattr(appointment, "duration_minutes", 30) or 30)
    return appointment.fecha + timedelta(minutes=duration_minutes)


async def _bg_update_calendar(appointment_id: int) -> None:
    if not get_calendar_service:
        return
    db = SessionLocal()
    try:
        appointment = await get_appointment(db, appointment_id)
        if not appointment or not appointment.google_calendar_id:
            return

        service = get_calendar_service()
        if not service:
            return

        calendar_id = os.getenv('GOOGLE_CALENDAR_ID', 'primary')
        service.update_event(
            calendar_id=calendar_id,
            event_id=appointment.google_calendar_id,
            title=f"Cita: {appointment.nombre}",
            description=f"Cita de agendamiento en Cirujano de Sintetizadores\n\n{appointment.mensaje or ''}",
            start_time=appointment.fecha,
            end_time=_appointment_end_time(appointment),
            attendee_email=appointment.email,
        )
    except Exception as e:
        print(f"Error updating Google Calendar event (background): {e}")
    finally:
        db.close()


async def _bg_delete_calendar_event(event_id: str) -> None:
    if not event_id or not get_calendar_service:
        return
    try:
        service = get_calendar_service()
        if not service:
            return
        calendar_id = os.getenv('GOOGLE_CALENDAR_ID', 'primary')
        service.delete_event(calendar_id=calendar_id, event_id=event_id)
    except Exception as e:
        print(f"Error deleting Google Calendar event (background): {e}")


def _should_skip_turnstile() -> bool:
    env = str(os.getenv("ENVIRONMENT") or "").strip().lower()
    return os.getenv("TURNSTILE_DISABLE", "false").lower() == "true" or env in {"test", "testing"}


@router.get("/public-availability")
async def get_public_availability(
    date: str = Query(..., description="Fecha local Chile en formato YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    """
    Retorna los bloques horarios ya ocupados para una fecha pública.

    El frontend agenda en hora Chile; por eso la fecha recibida se interpreta en
    America/Santiago y luego se normaliza a UTC para consultar la base.
    """
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Fecha inválida. Use YYYY-MM-DD.") from exc

    start_local = datetime(
        target_date.year,
        target_date.month,
        target_date.day,
        0,
        0,
        0,
        tzinfo=CL_TZ,
    )
    end_local = start_local + timedelta(days=1)

    appointments = await get_appointments_by_date_range(
        db,
        start_date=to_utc(start_local),
        end_date=to_utc(end_local),
    )

    occupied_slots = sorted(
        {
            to_local(appointment.fecha).strftime("%H:%M")
            for appointment in appointments
            if appointment.estado in {"pendiente", "confirmado"} and appointment.fecha
        }
    )

    return {"date": date, "occupied_slots": occupied_slots}


@router.post("/", response_model=AppointmentResponse, status_code=201)
@limiter.limit("5/minute")
async def create_appointment_endpoint(
    appointment: AppointmentCreate,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create a new appointment booking.

    - **nombre**: Customer full name (letters, accents, Ñ only)
    - **email**: Valid email address
    - **telefono**: Phone number starting with + followed by digits
    - **fecha**: Appointment date and time (must be in the future)
    - **mensaje**: Optional message or special requests
    """
    try:
        # Turnstile verification (public endpoint)
        if not _should_skip_turnstile():
            from app.services.turnstile_service import verify_turnstile
            if not appointment.turnstile_token or not verify_turnstile(appointment.turnstile_token, request.client.host if request.client else None):
                raise HTTPException(status_code=400, detail="Captcha inválido")

        # Create appointment in database
        db_appointment = await create_appointment(db, appointment)

        # Email y calendar en background — no bloquean la respuesta HTTP
        background_tasks.add_task(
            send_appointment_confirmation,
            email=db_appointment.email,
            nombre=db_appointment.nombre,
            fecha=db_appointment.fecha,
            appointment_id=db_appointment.id,
        )
        background_tasks.add_task(_bg_sync_calendar, db_appointment.id)

        return db_appointment

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment_endpoint(
    appointment_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("appointments", "read"))
):
    """Get appointment by ID"""
    db_appointment = await get_appointment(db, appointment_id)
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return db_appointment


@router.get("/", response_model=List[AppointmentResponse])
async def list_appointments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    estado: str = Query(None),
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("appointments", "read"))
):
    """
    List appointments with optional filtering.
    
    - **skip**: Number of appointments to skip
    - **limit**: Maximum number of appointments to return
    - **estado**: Filter by status (pendiente, confirmado, cancelado)
    """
    appointments = await get_appointments(db, skip=skip, limit=limit, estado=estado)
    return appointments


@router.get("/email/{email}", response_model=List[AppointmentResponse])
async def get_appointments_by_email_endpoint(
    email: str,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("appointments", "read"))
):
    """Get all appointments for a specific email"""
    appointments = await get_appointments_by_email(db, email)
    return appointments


@router.patch("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment_endpoint(
    appointment_id: int,
    appointment_update: AppointmentUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("appointments", "update"))
):
    """Update an appointment"""
    current_appointment = await get_appointment(db, appointment_id)
    if not current_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    existing_event_id = current_appointment.google_calendar_id
    fecha_changed = appointment_update.fecha is not None and appointment_update.fecha != current_appointment.fecha
    db_appointment = await update_appointment(db, appointment_id, appointment_update)
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if existing_event_id and db_appointment.estado == "cancelado":
        background_tasks.add_task(_bg_delete_calendar_event, existing_event_id)
    elif existing_event_id and (fecha_changed or appointment_update.mensaje is not None):
        background_tasks.add_task(_bg_update_calendar, appointment_id)

    return db_appointment


@router.delete("/{appointment_id}", status_code=204)
async def delete_appointment_endpoint(
    appointment_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("appointments", "delete"))
):
    """Delete an appointment"""
    current_appointment = await get_appointment(db, appointment_id)
    if not current_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    existing_event_id = current_appointment.google_calendar_id
    success = await delete_appointment(db, appointment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if existing_event_id:
        background_tasks.add_task(_bg_delete_calendar_event, existing_event_id)
    return None


@router.get("/status/pending", response_model=List[AppointmentResponse])
async def get_pending_appointments_endpoint(
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("appointments", "read"))
):
    """Get all pending appointments"""
    appointments = await get_pending_appointments(db)
    return appointments


@router.get("/status/confirmed", response_model=List[AppointmentResponse])
async def get_confirmed_appointments_endpoint(
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("appointments", "read"))
):
    """Get all confirmed appointments"""
    appointments = await get_confirmed_appointments(db)
    return appointments
