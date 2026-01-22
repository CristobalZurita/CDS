"""
Pydantic schemas for purchase requests (cart/suggestions).
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class PurchaseRequestItemCreate(BaseModel):
    product_id: Optional[int] = None
    sku: Optional[str] = None
    name: Optional[str] = None
    quantity: int = Field(1, ge=1)
    unit_price: Optional[float] = 0.0
    external_url: Optional[str] = None


class PurchaseRequestCreate(BaseModel):
    client_id: Optional[int] = None
    repair_id: Optional[int] = None
    notes: Optional[str] = None
    items: List[PurchaseRequestItemCreate] = []


class PurchaseRequestItemOut(BaseModel):
    id: int
    request_id: int
    product_id: Optional[int]
    sku: Optional[str]
    name: Optional[str]
    quantity: int
    unit_price: float
    external_url: Optional[str]
    status: str

    class Config:
        from_attributes = True


class PurchaseRequestOut(BaseModel):
    id: int
    client_id: Optional[int]
    repair_id: Optional[int]
    created_by: Optional[int]
    status: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    items: List[PurchaseRequestItemOut] = []

    class Config:
        from_attributes = True
