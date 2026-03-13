"""
Schemas para gestión dinámica de medios.
ADITIVO: no modifica schemas existentes.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class MediaAssetCreate(BaseModel):
    public_id: str
    secure_url: str
    folder: Optional[str] = None
    original_filename: Optional[str] = None
    format: Optional[str] = None
    bytes: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None


class MediaAssetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    public_id: str
    secure_url: str
    folder: Optional[str] = None
    original_filename: Optional[str] = None
    format: Optional[str] = None
    bytes: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    uploaded_at: datetime


class MediaBindingUpsert(BaseModel):
    asset_id: int
    label: Optional[str] = None


class MediaBindingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slot_key: str
    label: Optional[str] = None
    asset: MediaAssetOut
    updated_at: datetime
