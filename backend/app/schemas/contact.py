"""
Pydantic schemas for contact messages.
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime


class ContactCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    subject: str = Field(..., min_length=2, max_length=255)
    message: str = Field(..., min_length=2, max_length=2048)
    source_url: Optional[str] = None
    turnstile_token: Optional[str] = None


class ContactMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    subject: str
    message: str
    source_url: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status: str
    created_at: datetime
