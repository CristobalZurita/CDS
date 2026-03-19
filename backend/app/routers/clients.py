"""
Router de Clientes (Admin)
==========================
Endpoints para gestión de clientes desde admin.
Usa permisos granulares (require_permission).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import get_current_admin, require_permission
from app.models.client import Client
from app.models.device import Device
from app.models.repair import Repair
from app.services.repair_helpers import (
    auto_archive_repairs as _auto_archive_repairs,
    resolved_repair_code as _resolved_repair_code,
)

router = APIRouter(prefix="/clients", tags=["clients"])

def _client_code(client_id: int) -> str:
    return f"CDS-{client_id:03d}"


@router.get("", response_model=List[Dict])
@router.get("/", response_model=List[Dict])
def list_clients(
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("clients", "read"))
):
    clients = db.query(Client).all()
    payload = []
    for client in clients:
        payload.append({
            "id": client.id,
            "client_code": _client_code(client.id),
            "name": client.name,
            "email": client.email,
            "phone": client.phone,
            "phone_alt": client.phone_alt,
            "address": client.address,
            "city": client.city,
            "region": client.region,
            "country": client.country,
            "notes": client.notes,
            "internal_notes": client.internal_notes,
            "tax_id": client.tax_id,
            "company_name": client.company_name,
            "billing_address": client.billing_address,
            "customer_segment": client.customer_segment,
            "language_preference": client.language_preference,
            "service_preference": client.service_preference,
            "total_repairs": client.total_repairs,
            "total_spent": client.total_spent,
        })
    return payload


@router.get("/{client_id}", response_model=Dict)
def get_client(client_id: int, db: Session = Depends(get_db), user: dict = Depends(require_permission("clients", "read"))):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return {
        "id": client.id,
        "client_code": _client_code(client.id),
        "name": client.name,
        "email": client.email,
        "phone": client.phone,
        "phone_alt": client.phone_alt,
        "address": client.address,
        "city": client.city,
        "region": client.region,
        "country": client.country,
        "notes": client.notes,
        "internal_notes": client.internal_notes,
        "tax_id": client.tax_id,
        "company_name": client.company_name,
        "billing_address": client.billing_address,
        "customer_segment": client.customer_segment,
        "language_preference": client.language_preference,
        "service_preference": client.service_preference,
        "total_repairs": client.total_repairs,
        "total_spent": client.total_spent,
    }


@router.post("", status_code=status.HTTP_201_CREATED)
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_client(
    payload: Dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("clients", "create"))
):
    if not payload.get("name"):
        raise HTTPException(status_code=400, detail="Missing name")
    client = Client(
        name=payload.get("name"),
        email=payload.get("email"),
        phone=payload.get("phone"),
        phone_alt=payload.get("phone_alt"),
        address=payload.get("address"),
        city=payload.get("city"),
        region=payload.get("region"),
        country=payload.get("country") or "Chile",
        notes=payload.get("notes"),
        preferred_contact=payload.get("preferred_contact") or "whatsapp",
        internal_notes=payload.get("internal_notes"),
        tax_id=payload.get("tax_id"),
        company_name=payload.get("company_name"),
        billing_address=payload.get("billing_address"),
        customer_segment=payload.get("customer_segment") or "regular",
        language_preference=payload.get("language_preference") or "es",
        service_preference=payload.get("service_preference") or payload.get("preferred_contact") or "whatsapp",
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return {
        "id": client.id,
        "name": client.name,
        "client_code": _client_code(client.id),
        "email": client.email,
        "phone": client.phone,
        "city": client.city,
        "region": client.region,
    }


@router.put("/{client_id}")
def update_client(
    client_id: int,
    payload: Dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("clients", "update"))
):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    for key, value in payload.items():
        if hasattr(client, key):
            setattr(client, key, value)
    db.commit()
    db.refresh(client)
    return {"ok": True}


@router.delete("/{client_id}")
def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("clients", "delete"))
):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    db.delete(client)
    db.commit()
    return {"ok": True}


@router.get("/{client_id}/devices", response_model=List[Dict])
def list_client_devices(client_id: int, db: Session = Depends(get_db), user: dict = Depends(require_permission("clients", "read"))):
    devices = db.query(Device).filter(Device.client_id == client_id).all()
    return [
        {
            "id": d.id,
            "model": d.model,
            "serial_number": d.serial_number,
            "brand_other": d.brand_other,
            "description": d.description,
            "condition_notes": d.condition_notes,
        }
        for d in devices
    ]


@router.get("/{client_id}/repairs", response_model=List[Dict])
def list_client_repairs(client_id: int, db: Session = Depends(get_db), user: dict = Depends(require_permission("clients", "read"))):
    _auto_archive_repairs(db)
    repairs = (
        db.query(Repair)
        .join(Device, Device.id == Repair.device_id)
        .filter(Device.client_id == client_id)
        .filter(Repair.archived_at.is_(None))
        .all()
    )
    payload = []
    for repair in repairs:
        payload.append({
            "id": repair.id,
            "repair_number": repair.repair_number,
            "repair_code": _resolved_repair_code(repair, client_id),
            "ot_parent_id": repair.ot_parent_id,
            "ot_sequence": repair.ot_sequence,
            "status_id": repair.status_id,
            "problem_reported": repair.problem_reported,
            "created_at": repair.created_at.isoformat() if repair.created_at else None,
            "device_id": repair.device_id
        })
    return payload


@router.get("/code/next", response_model=Dict)
@router.get("/next-code", response_model=Dict)
def get_next_client_code(db: Session = Depends(get_db), user: dict = Depends(require_permission("clients", "read"))):
    last = db.query(Client).order_by(Client.id.desc()).first()
    next_id = (last.id + 1) if last else 1
    return {"next_client_id": next_id, "client_code": _client_code(next_id)}
