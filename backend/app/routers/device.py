from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.dependencies import require_permission
from app.models.device import Device
from app.models.device_lookup import DeviceType
from app.models.client import Client
from app.schemas.device import (
    DeviceCreate,
    DeviceCreatedResponse,
    DeviceListItem,
    DeviceRead,
    DeviceUpdate,
    OkResponse,
)

router = APIRouter(prefix="/devices", tags=["devices"])


def _ensure_default_type(db: Session) -> DeviceType:
    dt = db.query(DeviceType).first()
    if not dt:
        dt = DeviceType(code="generic", name="Generic", description="Autocreated")
        db.add(dt)
        db.commit()
        db.refresh(dt)
    return dt


@router.get("/", response_model=List[DeviceListItem])
def list_devices(db: Session = Depends(get_db), user: dict = Depends(require_permission("devices", "read"))):
    devices = db.query(Device).all()
    return [
        {
            "id": d.id,
            "client_id": d.client_id,
            "model": d.model,
            "serial_number": d.serial_number,
            "year_manufactured": d.year_manufactured,
            "brand_other": d.brand_other,
        }
        for d in devices
    ]


@router.get("/{device_id}", response_model=DeviceRead)
def get_device(device_id: int, db: Session = Depends(get_db), user: dict = Depends(require_permission("devices", "read"))):
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
        "year_manufactured": device.year_manufactured,
        "description": device.description,
        "condition_notes": device.condition_notes,
        "brand_other": device.brand_other,
    }


@router.post("/", response_model=DeviceCreatedResponse, status_code=status.HTTP_201_CREATED)
def create_device(
    payload: DeviceCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("devices", "create"))
):
    data = payload.model_dump()
    client_id = data.get("client_id")
    if not client_id:
        raise HTTPException(status_code=400, detail="client_id required")
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    device_type_id = data.get("device_type_id")
    if not device_type_id:
        device_type_id = _ensure_default_type(db).id

    description_value = data.get("description")
    accessories = data.get("accessories")
    if accessories:
        accessories_line = f"Accesorios: {accessories}"
        description_value = f"{description_value}\n{accessories_line}" if description_value else accessories_line

    device = Device(
        client_id=client_id,
        device_type_id=device_type_id,
        brand_id=data.get("brand_id"),
        brand_other=data.get("brand_other"),
        model=data.get("model") or "Unknown",
        serial_number=data.get("serial_number"),
        year_manufactured=data.get("year_manufactured"),
        description=description_value,
        condition_notes=data.get("condition_notes"),
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    return {"id": device.id}


@router.put("/{device_id}", response_model=OkResponse)
def update_device(
    device_id: int,
    payload: DeviceUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("devices", "update"))
):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    updates = payload.model_dump(exclude_unset=True)
    updates.pop("accessories", None)
    for key, value in updates.items():
        if hasattr(device, key):
            setattr(device, key, value)
    db.commit()
    db.refresh(device)
    return {"ok": True}


@router.delete("/{device_id}", response_model=OkResponse)
def delete_device(device_id: int, db: Session = Depends(get_db), user: dict = Depends(require_permission("devices", "delete"))):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    db.delete(device)
    db.commit()
    return {"ok": True}
