"""
Router for Appointment endpoints
Handles appointment booking and management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from backend.app.core.database import get_db
from backend.app.crud.appointment import (
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
from backend.app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse
)
from backend.app.services.email_service import send_appointment_confirmation
from backend.app.services.google_calendar_service import sync_to_google_calendar

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("/", response_model=AppointmentResponse, status_code=201)
async def create_appointment_endpoint(
    appointment: AppointmentCreate,
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
        # Create appointment in database
        db_appointment = await create_appointment(db, appointment)
        
        # Send confirmation email
        try:
            await send_appointment_confirmation(
                email=db_appointment.email,
                nombre=db_appointment.nombre,
                fecha=db_appointment.fecha,
                appointment_id=db_appointment.id
            )
        except Exception as e:
            print(f"Error sending email: {e}")
            # Don't fail the appointment creation if email fails
        
        # Sync to Google Calendar
        try:
            calendar_id = await sync_to_google_calendar(db_appointment)
            if calendar_id:
                db_appointment.google_calendar_id = calendar_id
                await update_appointment(
                    db, 
                    db_appointment.id, 
                    AppointmentUpdate(google_calendar_id=calendar_id)
                )
        except Exception as e:
            print(f"Error syncing to Google Calendar: {e}")
            # Don't fail the appointment creation if calendar sync fails
        
        return db_appointment
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment_endpoint(
    appointment_id: int,
    db: Session = Depends(get_db)
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
    db: Session = Depends(get_db)
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
    db: Session = Depends(get_db)
):
    """Get all appointments for a specific email"""
    appointments = await get_appointments_by_email(db, email)
    return appointments


@router.patch("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment_endpoint(
    appointment_id: int,
    appointment_update: AppointmentUpdate,
    db: Session = Depends(get_db)
):
    """Update an appointment"""
    db_appointment = await update_appointment(db, appointment_id, appointment_update)
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return db_appointment


@router.delete("/{appointment_id}", status_code=204)
async def delete_appointment_endpoint(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    """Delete an appointment"""
    success = await delete_appointment(db, appointment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return None


@router.get("/status/pending", response_model=List[AppointmentResponse])
async def get_pending_appointments_endpoint(
    db: Session = Depends(get_db)
):
    """Get all pending appointments"""
    appointments = await get_pending_appointments(db)
    return appointments


@router.get("/status/confirmed", response_model=List[AppointmentResponse])
async def get_confirmed_appointments_endpoint(
    db: Session = Depends(get_db)
):
    """Get all confirmed appointments"""
    appointments = await get_confirmed_appointments(db)
    return appointments
