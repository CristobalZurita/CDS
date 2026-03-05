"""Schemas for instrument routers."""
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class InstrumentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    model: str = Field(..., min_length=1, max_length=255)
    brand_id: Optional[int] = None
    type: Optional[str] = Field(default=None, max_length=100)
    year: Optional[int] = None
    description: Optional[str] = None
    valor_estimado: Optional[int] = None
    image: Optional[Dict[str, Any]] = None
    photo_base_url: Optional[str] = Field(default=None, max_length=512)
    template_json: Optional[Dict[str, Any]] = None
    mapping_status: Optional[str] = Field(default=None, max_length=50)
    family: Optional[str] = Field(default=None, max_length=50)


class InstrumentUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    model: Optional[str] = Field(default=None, min_length=1, max_length=255)
    brand_id: Optional[int] = None
    type: Optional[str] = Field(default=None, max_length=100)
    year: Optional[int] = None
    description: Optional[str] = None
    valor_estimado: Optional[int] = None
    image: Optional[Dict[str, Any]] = None
    photo_base_url: Optional[str] = Field(default=None, max_length=512)
    template_json: Optional[Dict[str, Any]] = None
    mapping_status: Optional[str] = Field(default=None, max_length=50)
    family: Optional[str] = Field(default=None, max_length=50)


class InstrumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    brand_id: Optional[int] = None
    name: str
    model: str
    type: Optional[str] = None
    year: Optional[int] = None
    description: Optional[str] = None
    valor_estimado: Optional[int] = None
    image: Optional[Dict[str, Any]] = None
    photo_base_url: Optional[str] = None
    template_json: Optional[Dict[str, Any]] = None
    mapping_status: Optional[str] = None
    family: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class OkResponse(BaseModel):
    ok: bool
