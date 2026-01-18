from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.models.device import Device
from app.models.device_lookup import DeviceType, DeviceBrand
from app.models.client import Client

router = APIRouter(prefix="/devices", tags=["devices"])


def _ensure_default_type(db: Session) -> DeviceType:
    dt = db.query(DeviceType).first()
    if not dt:
        dt = DeviceType(code="generic", name="Generic", description="Autocreated")
        db.add(dt)
        db.commit()
        db.refresh(dt)
    return dt


@router.get("/", response_model=List[Dict])
def list_devices(db: Session = Depends(get_db), admin: dict = Depends(get_current_admin)):
    devices = db.query(Device).all()
    return [{"id": d.id, "client_id": d.client_id, "model": d.model, "serial_number": d.serial_number} for d in devices]


@router.get("/{device_id}", response_model=Dict)
def get_device(device_id: int, db: Session = Depends(get_db), admin: dict = Depends(get_current_admin)):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return {
        "id": device.id,
        "client_id": device.client_id,
        "device_type_id": device.device_type_id,
        "brand_id": device.brand_id,
        "model": device.model,
        "serial_number": device.serial_number,
        "description": device.description,
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_device(payload: Dict, db: Session = Depends(get_db), admin: dict = Depends(get_current_admin)):
    client_id = payload.get("client_id")
    if not client_id:
        raise HTTPException(status_code=400, detail="client_id required")
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    device_type_id = payload.get("device_type_id")
    if not device_type_id:
        device_type_id = _ensure_default_type(db).id

    device = Device(
        client_id=client_id,
        device_type_id=device_type_id,
        brand_id=payload.get("brand_id"),
        brand_other=payload.get("brand_other"),
        model=payload.get("model") or "Unknown",
        serial_number=payload.get("serial_number"),
        description=payload.get("description"),
        condition_notes=payload.get("condition_notes"),
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    return {"id": device.id}


@router.put("/{device_id}")
def update_device(device_id: int, payload: Dict, db: Session = Depends(get_db), admin: dict = Depends(get_current_admin)):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    for key, value in payload.items():
        if hasattr(device, key):
            setattr(device, key, value)
    db.commit()
    db.refresh(device)
    return {"ok": True}


@router.delete("/{device_id}")
def delete_device(device_id: int, db: Session = Depends(get_db), admin: dict = Depends(get_current_admin)):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    db.delete(device)
    db.commit()
    return {"ok": True}
