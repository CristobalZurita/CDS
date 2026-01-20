"""
Router de Clientes (Admin)
==========================
Endpoints para gestión de clientes desde admin.
Usa permisos granulares (require_permission).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict

from app.core.database import get_db
from app.core.dependencies import get_current_admin, require_permission
from app.models.client import Client
from app.models.device import Device

router = APIRouter(prefix="/clients", tags=["clients"])


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
            "name": client.name,
            "email": client.email,
            "phone": client.phone,
            "address": client.address,
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
        "name": client.name,
        "email": client.email,
        "phone": client.phone,
        "address": client.address,
        "notes": client.notes,
        "total_repairs": client.total_repairs,
        "total_spent": client.total_spent,
    }


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
        address=payload.get("address"),
        notes=payload.get("notes"),
        preferred_contact=payload.get("preferred_contact") or "whatsapp",
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return {"id": client.id, "name": client.name}


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
    return [{"id": d.id, "model": d.model, "serial_number": d.serial_number} for d in devices]
