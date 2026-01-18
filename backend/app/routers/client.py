from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, List

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.client import Client
from app.models.device import Device
from app.models.device_lookup import DeviceBrand
from app.models.repair import Repair, RepairStatus
from app.models.repair_note import RepairNote
from app.models.repair_photo import RepairPhoto

router = APIRouter(prefix="/client", tags=["client"])


def _split_full_name(full_name: str) -> tuple[str | None, str | None]:
    parts = (full_name or "").strip().split()
    if not parts:
        return None, None
    if len(parts) == 1:
        return parts[0], None
    return parts[0], " ".join(parts[1:])


def _ensure_client(db: Session, user: User) -> Client:
    client = db.query(Client).filter(Client.user_id == user.id).first()
    if client:
        return client
    client = Client(
        user_id=user.id,
        name=user.full_name,
        email=user.email,
        phone=user.phone
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def _status_code(repair: Repair) -> str:
    if repair.status_obj and repair.status_obj.code:
        return repair.status_obj.code
    fallback = {
        1: "pending",
        2: "in_progress",
        3: "completed",
        4: "delivered",
    }
    return fallback.get(repair.status_id, "pending")


def _status_progress(code: str) -> int:
    mapping = {
        "pending_quote": 10,
        "quoted": 20,
        "approved": 30,
        "in_progress": 60,
        "waiting_parts": 35,
        "testing": 80,
        "completed": 100,
        "delivered": 100,
        "cancelled": 0,
    }
    return mapping.get(code, 10)


def _device_label(db: Session, device: Device) -> str:
    if not device:
        return "Equipo"
    brand = None
    if device.brand_other:
        brand = device.brand_other
    elif device.brand_id:
        brand_row = db.query(DeviceBrand).filter(DeviceBrand.id == device.brand_id).first()
        brand = brand_row.name if brand_row else None
    if brand:
        return f"{brand} {device.model}"
    return device.model


def _timeline_from_repair(repair: Repair) -> List[Dict]:
    timeline = []
    fields = [
        ("intake_date", "Ingreso recibido"),
        ("diagnosis_date", "Diagnóstico"),
        ("approval_date", "Aprobación"),
        ("start_date", "Reparación iniciada"),
        ("completion_date", "Reparación completada"),
        ("delivery_date", "Equipo entregado"),
    ]
    for field, label in fields:
        value = getattr(repair, field, None)
        if value:
            timeline.append({"label": label, "date": value})
    timeline.sort(key=lambda x: x["date"])
    return timeline


@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    user_obj = db.query(User).filter(User.id == int(user["user_id"])).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    client = _ensure_client(db, user_obj)

    repairs = (
        db.query(Repair)
        .join(Device, Repair.device_id == Device.id)
        .filter(Device.client_id == client.id)
        .order_by(Repair.updated_at.desc())
        .all()
    )

    pending_codes = {"pending_quote", "quoted", "approved"}
    active_codes = {"in_progress", "waiting_parts", "testing"}
    completed_codes = {"completed", "delivered"}

    pending_repairs = 0
    active_repairs = 0
    completed_repairs = 0
    total_spent = 0.0
    active_list = []

    for repair in repairs:
        code = _status_code(repair)
        if code in pending_codes:
            pending_repairs += 1
        elif code in active_codes:
            active_repairs += 1
        elif code in completed_codes:
            completed_repairs += 1

        if code in completed_codes and repair.total_cost:
            total_spent += repair.total_cost

        if code in active_codes:
            active_list.append({
                "id": repair.id,
                "repair_number": repair.repair_number,
                "instrument": _device_label(db, repair.device),
                "fault": repair.problem_reported,
                "status": code,
                "date_in": repair.intake_date,
                "estimated_completion": repair.completion_date,
                "progress": _status_progress(code),
            })

    return {
        "user": {
            "id": user_obj.id,
            "email": user_obj.email,
            "full_name": user_obj.full_name,
            "phone": user_obj.phone,
            "role": user_obj.role,
        },
        "stats": {
            "pending_repairs": pending_repairs,
            "active_repairs": active_repairs,
            "completed_repairs": completed_repairs,
            "total_spent": round(total_spent, 2),
        },
        "active_repairs": active_list,
        "notifications": [],
    }


@router.get("/repairs")
def list_client_repairs(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    user_obj = db.query(User).filter(User.id == int(user["user_id"])).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    client = _ensure_client(db, user_obj)
    repairs = (
        db.query(Repair)
        .join(Device, Repair.device_id == Device.id)
        .filter(Device.client_id == client.id)
        .order_by(Repair.updated_at.desc())
        .all()
    )

    payload = []
    for repair in repairs:
        code = _status_code(repair)
        payload.append({
            "id": repair.id,
            "repair_number": repair.repair_number,
            "instrument": _device_label(db, repair.device),
            "fault": repair.problem_reported,
            "status": code,
            "date_in": repair.intake_date,
            "date_out": repair.delivery_date or repair.completion_date,
            "cost": repair.total_cost,
            "progress": _status_progress(code),
        })

    return payload


@router.get("/repairs/{repair_id}/timeline")
def get_repair_timeline(repair_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    user_obj = db.query(User).filter(User.id == int(user["user_id"])).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    client = _ensure_client(db, user_obj)
    repair = (
        db.query(Repair)
        .join(Device, Repair.device_id == Device.id)
        .filter(Device.client_id == client.id, Repair.id == repair_id)
        .first()
    )
    if not repair:
        raise HTTPException(status_code=404, detail="Reparación no encontrada")

    return {
        "repair_id": repair.id,
        "repair_number": repair.repair_number,
        "status": _status_code(repair),
        "timeline": _timeline_from_repair(repair),
    }


@router.get("/repairs/{repair_id}/details")
def get_repair_details(repair_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    user_obj = db.query(User).filter(User.id == int(user["user_id"])).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    client = _ensure_client(db, user_obj)
    repair = (
        db.query(Repair)
        .join(Device, Repair.device_id == Device.id)
        .filter(Device.client_id == client.id, Repair.id == repair_id)
        .first()
    )
    if not repair:
        raise HTTPException(status_code=404, detail="Reparación no encontrada")

    photos = (
        db.query(RepairPhoto)
        .filter(RepairPhoto.repair_id == repair.id, RepairPhoto.visible_to_client == 1)
        .order_by(RepairPhoto.sort_order.asc(), RepairPhoto.created_at.desc())
        .all()
    )
    notes = (
        db.query(RepairNote)
        .filter(RepairNote.repair_id == repair.id, RepairNote.note_type != "internal")
        .order_by(RepairNote.created_at.desc())
        .all()
    )

    return {
        "repair": {
            "id": repair.id,
            "repair_number": repair.repair_number,
            "instrument": _device_label(db, repair.device),
            "status": _status_code(repair),
            "problem_reported": repair.problem_reported,
            "diagnosis": repair.diagnosis,
            "work_performed": repair.work_performed,
            "total_cost": repair.total_cost,
        },
        "timeline": _timeline_from_repair(repair),
        "photos": [
            {
                "id": p.id,
                "photo_url": p.photo_url,
                "photo_type": p.photo_type,
                "caption": p.caption,
                "created_at": p.created_at,
            }
            for p in photos
        ],
        "notes": [
            {
                "id": n.id,
                "note": n.note,
                "note_type": n.note_type,
                "created_at": n.created_at,
            }
            for n in notes
        ],
    }


@router.get("/profile")
def get_profile(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    user_obj = db.query(User).filter(User.id == int(user["user_id"])).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    client = _ensure_client(db, user_obj)

    return {
        "email": user_obj.email,
        "full_name": user_obj.full_name,
        "phone": user_obj.phone,
        "address": client.address,
        "member_since": user_obj.created_at,
        "stats": {
            "total_repairs": client.total_repairs,
            "total_spent": client.total_spent,
        },
    }


@router.put("/profile")
def update_profile(payload: Dict, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    user_obj = db.query(User).filter(User.id == int(user["user_id"])).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    client = _ensure_client(db, user_obj)

    email = payload.get("email")
    full_name = payload.get("full_name")
    phone = payload.get("phone")
    address = payload.get("address")

    if email and email != user_obj.email:
        existing = db.query(User).filter(User.email == email).first()
        if existing and existing.id != user_obj.id:
            raise HTTPException(status_code=400, detail="Email ya registrado")
        user_obj.email = email
        client.email = email

    if full_name is not None:
        first_name, last_name = _split_full_name(full_name)
        user_obj.first_name = first_name
        user_obj.last_name = last_name
        client.name = full_name or client.name

    if phone is not None:
        user_obj.phone = phone
        client.phone = phone

    if address is not None:
        client.address = address

    db.add(user_obj)
    db.add(client)
    db.commit()
    db.refresh(user_obj)
    db.refresh(client)

    return {
        "email": user_obj.email,
        "full_name": user_obj.full_name,
        "phone": user_obj.phone,
        "address": client.address,
        "member_since": user_obj.created_at,
        "stats": {
            "total_repairs": client.total_repairs,
            "total_spent": client.total_spent,
        },
    }
