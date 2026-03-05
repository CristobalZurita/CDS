"""Schemas for Repair."""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime, date


class RepairBase(BaseModel):
    repair_number: Optional[str] = None
    device_id: int
    quote_id: Optional[int] = None
    status_id: Optional[int] = None
    assigned_to: Optional[int] = None
    problem_reported: str = Field(..., min_length=2)
    diagnosis: Optional[str] = None
    work_performed: Optional[str] = None
    parts_cost: Optional[float] = 0
    labor_cost: Optional[float] = 0
    additional_cost: Optional[float] = 0
    discount: Optional[float] = 0
    total_cost: Optional[float] = 0
    payment_status: Optional[str] = None
    payment_method: Optional[str] = None
    paid_amount: Optional[float] = 0
    warranty_days: Optional[int] = 90
    warranty_until: Optional[date] = None
    priority: Optional[int] = 2


class RepairCreate(RepairBase):
    pass


class RepairUpdate(BaseModel):
    status_id: Optional[int] = None
    assigned_to: Optional[int] = None
    diagnosis: Optional[str] = None
    work_performed: Optional[str] = None
    parts_cost: Optional[float] = None
    labor_cost: Optional[float] = None
    additional_cost: Optional[float] = None
    discount: Optional[float] = None
    total_cost: Optional[float] = None
    payment_status: Optional[str] = None
    payment_method: Optional[str] = None
    paid_amount: Optional[float] = None
    warranty_days: Optional[int] = None
    warranty_until: Optional[date] = None
    priority: Optional[int] = None


class RepairRead(RepairBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
