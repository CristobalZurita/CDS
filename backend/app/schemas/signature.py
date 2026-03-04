"""
Pydantic schemas for signature requests.
"""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class SignatureRequestCreate(BaseModel):
    repair_id: int
    request_type: str = Field(..., pattern="^(ingreso|retiro)$")
    expires_minutes: Optional[int] = 15


class SignatureSubmit(BaseModel):
    token: str
    image_base64: str  # data:image/png;base64,....


class SignatureRequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    repair_id: int
    request_type: str
    token: str
    status: str
    created_at: datetime
    signed_at: Optional[datetime]
    expires_at: Optional[datetime]
