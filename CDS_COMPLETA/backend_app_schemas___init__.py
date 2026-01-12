"""
Pydantic schemas for request/response validation
Define DTOs (Data Transfer Objects) for API endpoints
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional, Dict, ClassVar
from datetime import datetime


# ============= BRAND =============
class BrandBase(BaseModel):
    id: str
    name: str
    tier: str
    founded: int
    country: str
    description: str


class BrandRead(BrandBase):
    pass

    class Config:
        from_attributes = True


# ============= INSTRUMENT =============
class InstrumentBase(BaseModel):
    id: str
    brand_id: str
    model: str
    type: str
    year: int
    description: str
    components: Optional[Dict] = None
    valor_min: Optional[float] = None
    valor_max: Optional[float] = None
    fallas_comunes: Optional[List[str]] = None
    imagen_url: Optional[str] = None
    manual_url: Optional[str] = None


class InstrumentRead(InstrumentBase):
    created_at: datetime

    class Config:
        from_attributes = True


# ============= FAULT =============
class FaultBase(BaseModel):
    id: str
    name: str
    description: str
    base_price: float
    is_precedence: bool = False


class FaultRead(FaultBase):
    created_at: datetime

    class Config:
        from_attributes = True


# ============= DIAGNOSTIC =============
class DiagnosticCreate(BaseModel):
    client_name: str = Field(..., min_length=2, max_length=100)
    client_email: EmailStr
    client_phone: Optional[str] = None
    brand_id: str
    instrument_id: str
    faults_json: Dict[str, bool]
    estimated_cost: float
    notes: Optional[str] = None


class DiagnosticRead(BaseModel):
    id: int
    client_name: str
    client_email: str
    client_phone: Optional[str]
    brand_id: str
    instrument_id: str
    faults_json: Dict
    estimated_cost: float
    status: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============= REPAIR =============
class RepairDetailRead(BaseModel):
    id: int
    repair_id: int
    fault_id: str
    description: Optional[str]
    parts_used: Optional[Dict]
    created_at: datetime

    class Config:
        from_attributes = True


class RepairCreate(BaseModel):
    diagnostic_id: Optional[int] = None
    instrument_id: str
    brand_id: str
    client_name: str
    client_email: str
    actual_cost: float
    hours_worked: Optional[float] = None
    notes: Optional[str] = None
    completed_at: Optional[datetime] = None


class RepairRead(BaseModel):
    id: int
    diagnostic_id: Optional[int]
    instrument_id: str
    brand_id: str
    client_name: str
    client_email: str
    actual_cost: float
    hours_worked: Optional[float]
    notes: Optional[str]
    completed_at: Optional[datetime]
    created_at: datetime
    details: List[RepairDetailRead] = []

    class Config:
        from_attributes = True


# ============= API RESPONSE =============
class APIResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool
    message: str
    data: Optional[Dict] = None
    errors: Optional[List[str]] = None


class QuoteEstimate(BaseModel):
    """Cotización estimada"""
    base_cost: float
    complexity_factor: float
    value_factor: float
    final_cost: float
    brand_tier: str


# ============= PAYMENT =============
class PaymentCreate(BaseModel):
    repair_id: int
    amount: int = Field(..., gt=0)
    payment_method: str
    transaction_id: Optional[str] = None
    user_id: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None

    ALLOWED_METHODS: ClassVar[set] = {"card", "cash", "transfer", "paypal"}

    @field_validator("payment_method")
    def check_method(cls, v: str):
        if v not in cls.ALLOWED_METHODS:
            raise ValueError(f"Unsupported payment method: {v}")
        return v


class PaymentRead(BaseModel):
    id: int
    user_id: Optional[int]
    repair_id: Optional[int]
    amount: int
    payment_method: str
    transaction_id: Optional[str]
    status: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
