"""
Pydantic schemas for manual documents.
"""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class ManualCreate(BaseModel):
    instrument_id: int
    title: str = Field(..., min_length=2, max_length=255)
    source: str = Field("internal")
    url: Optional[str] = None
    file_path: Optional[str] = None


class ManualOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    instrument_id: int
    title: str
    source: str
    url: Optional[str]
    file_path: Optional[str]
    created_at: datetime
    updated_at: datetime
