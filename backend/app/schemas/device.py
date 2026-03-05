"""Schemas for device routers."""
from datetime import date
from typing import Optional

from pydantic import BaseModel


class DeviceListItem(BaseModel):
    id: int
    client_id: int
    model: str
    serial_number: Optional[str] = None
    year_manufactured: Optional[int] = None
    brand_other: Optional[str] = None


class DeviceRead(DeviceListItem):
    device_type_id: int
    brand_id: Optional[int] = None
    description: Optional[str] = None
    condition_notes: Optional[str] = None


class DeviceCreate(BaseModel):
    client_id: int
    device_type_id: Optional[int] = None
    brand_id: Optional[int] = None
    brand_other: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    year_manufactured: Optional[int] = None
    description: Optional[str] = None
    condition_notes: Optional[str] = None
    accessories: Optional[str] = None


class DeviceUpdate(BaseModel):
    client_id: Optional[int] = None
    device_type_id: Optional[int] = None
    brand_id: Optional[int] = None
    brand_other: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    year_manufactured: Optional[int] = None
    description: Optional[str] = None
    condition_notes: Optional[str] = None
    photos: Optional[str] = None
    total_repairs: Optional[int] = None
    first_repair_date: Optional[date] = None
    last_repair_date: Optional[date] = None
    accessories: Optional[str] = None


class DeviceCreatedResponse(BaseModel):
    id: int


class OkResponse(BaseModel):
    ok: bool
