"""Schemas for repair status routers."""
from typing import Optional

from pydantic import BaseModel, Field


class RepairStatusRead(BaseModel):
    id: int
    code: str
    name: str
    color: Optional[str] = None


class RepairStatusCreate(BaseModel):
    code: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    color: Optional[str] = None
    sort_order: int = 0


class RepairStatusUpdate(BaseModel):
    code: Optional[str] = Field(default=None, min_length=1)
    name: Optional[str] = Field(default=None, min_length=1)
    description: Optional[str] = None
    color: Optional[str] = None
    sort_order: Optional[int] = None


class RepairStatusCreatedResponse(BaseModel):
    id: int


class OkResponse(BaseModel):
    ok: bool
