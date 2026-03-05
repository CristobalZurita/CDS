"""
Pydantic schemas for tickets.
"""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime


class TicketCreate(BaseModel):
    client_id: Optional[int] = None
    repair_id: Optional[int] = None
    subject: str = Field(..., min_length=3, max_length=255)
    message: str = Field(..., min_length=1, max_length=5000)
    priority: Optional[str] = Field("normal")


class TicketMessageCreate(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)


class TicketMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: int
    author_id: Optional[int]
    body: str
    created_at: datetime


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    client_id: Optional[int]
    repair_id: Optional[int]
    created_by: Optional[int]
    subject: str
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime
    messages: List[TicketMessageOut] = []
