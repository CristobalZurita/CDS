"""
CRUD operations for Appointment model
Database operations for appointments
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from backend.app.models.appointment import Appointment
from backend.app.schemas.appointment import AppointmentCreate, AppointmentUpdate
from typing import List, Optional


async def create_appointment(db: Session, appointment: AppointmentCreate) -> Appointment:
    """Create a new appointment"""
    db_appointment = Appointment(
        nombre=appointment.nombre,
        email=appointment.email,
        telefono=appointment.telefono,
        fecha=appointment.fecha,
        mensaje=appointment.mensaje,
        estado="pendiente"
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment


async def get_appointment(db: Session, appointment_id: int) -> Optional[Appointment]:
    """Get appointment by ID"""
    return db.query(Appointment).filter(Appointment.id == appointment_id).first()


async def get_appointments(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    estado: Optional[str] = None
) -> List[Appointment]:
    """Get appointments with optional filtering"""
    query = db.query(Appointment)
    
    if estado:
        query = query.filter(Appointment.estado == estado)
    
    return query.order_by(desc(Appointment.created_at)).offset(skip).limit(limit).all()


async def get_appointments_by_email(db: Session, email: str) -> List[Appointment]:
    """Get appointments for a specific email"""
    return db.query(Appointment).filter(Appointment.email == email).order_by(
        desc(Appointment.created_at)
    ).all()


async def get_appointments_by_date_range(
    db: Session, 
    start_date: datetime, 
    end_date: datetime
) -> List[Appointment]:
    """Get appointments within a date range"""
    return db.query(Appointment).filter(
        Appointment.fecha >= start_date,
        Appointment.fecha <= end_date
    ).order_by(Appointment.fecha).all()


async def update_appointment(
    db: Session, 
    appointment_id: int, 
    appointment_update: AppointmentUpdate
) -> Optional[Appointment]:
    """Update an appointment"""
    db_appointment = await get_appointment(db, appointment_id)
    if not db_appointment:
        return None
    
    update_data = appointment_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_appointment, field, value)
    
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment


async def delete_appointment(db: Session, appointment_id: int) -> bool:
    """Delete an appointment"""
    db_appointment = await get_appointment(db, appointment_id)
    if not db_appointment:
        return False
    
    db.delete(db_appointment)
    db.commit()
    return True


async def get_pending_appointments(db: Session) -> List[Appointment]:
    """Get all pending appointments"""
    return db.query(Appointment).filter(
        Appointment.estado == "pendiente"
    ).order_by(Appointment.fecha).all()


async def get_confirmed_appointments(db: Session) -> List[Appointment]:
    """Get all confirmed appointments"""
    return db.query(Appointment).filter(
        Appointment.estado == "confirmado"
    ).order_by(Appointment.fecha).all()
