"""
Data models for Cirujano de Sintetizadores
Pydantic models for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


# Enums
class RepairStatus(str, Enum):
    """Estados posibles de una reparación"""
    INGRESADO = "INGRESADO"
    EN_DIAGNOSTICO = "EN_DIAGNOSTICO"
    ESPERANDO_REPUESTO = "ESPERANDO_REPUESTO"
    EN_REPARACION = "EN_REPARACION"
    FINALIZADO = "FINALIZADO"
    ENTREGADO = "ENTREGADO"


class InstrumentTier(str, Enum):
    """Niveles de complejidad de instrumentos"""
    LEGENDARY = "legendary"
    PROFESSIONAL = "professional"
    STANDARD = "standard"
    SPECIALIZED = "specialized"
    BOUTIQUE = "boutique"
    HISTORIC = "historic"


class FaultCategory(str, Enum):
    """Categorías de fallas"""
    CRITICAL = "critical"
    KEYBOARD = "keyboard"
    CONTROLS = "controls"
    AUDIO = "audio"
    SYNTHESIS = "synthesis"
    DISPLAY = "display"
    CONNECTIVITY = "connectivity"
    COMPONENTS = "components"
    MECHANICAL = "mechanical"
    COSMETIC = "cosmetic"
    POWER = "power"


# Base Models

class ClientBase(BaseModel):
    """Base client information"""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)


class ClientCreate(ClientBase):
    """Client creation model"""
    pass


class ClientResponse(ClientBase):
    """Client response model"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Equipment/Instrument Models

class EquipmentValue(BaseModel):
    """Equipment estimated value"""
    min: int = Field(..., gt=0)
    max: int = Field(..., gt=0)
    currency: str = "CLP"


class Components(BaseModel):
    """Instrument components specification"""
    encoders_rotativos: int = 0
    botones: int = 0
    lcd: bool = False
    leds: int = 0
    usb: bool = False
    midi_din: bool = False
    salidas_audio: int = 0
    faders: int = 0
    aftertouch: bool = False
    rueda_pitch: bool = False
    pedal: bool = False


class InstrumentBase(BaseModel):
    """Base instrument information"""
    brand: str
    model: str
    type: str
    year: int
    description: Optional[str] = None
    components: Components
    valor_estimado: EquipmentValue
    imagen_url: Optional[str] = None
    manual_url: Optional[str] = None


class InstrumentCreate(InstrumentBase):
    """Instrument creation model"""
    pass


class InstrumentResponse(InstrumentBase):
    """Instrument response model"""
    id: int

    class Config:
        from_attributes = True


# Fault/Diagnostic Models

class FaultBase(BaseModel):
    """Base fault information"""
    id: str
    name: str
    category: FaultCategory
    description: str
    base_price: int = Field(..., gt=0)


class DiagnosticInput(BaseModel):
    """Input for diagnostic wizard"""
    client: ClientCreate
    equipment: Dict
    faults: List[str]


class DiagnosticResult(BaseModel):
    """Result of diagnostic with quote"""
    equipment_info: Dict
    faults: List[str]
    base_cost: int
    complexity_factor: float
    value_factor: float
    final_cost: int


# Quote Models

class QuoteCreate(BaseModel):
    """Quote creation model"""
    client: ClientCreate
    equipment_info: Dict
    faults: List[str]
    estimated_cost: int


class QuoteResponse(BaseModel):
    """Quote response model"""
    id: int
    client_id: int
    equipment_info: Dict
    faults: List[str]
    estimated_cost: int
    final_cost: Optional[int] = None
    status: str = "pending"
    created_at: datetime
    notes: Optional[str] = None

    class Config:
        from_attributes = True


# Repair/Case Models

class RepairCreate(BaseModel):
    """Repair case creation from quote"""
    quote_id: int
    technical_notes: Optional[str] = None


class RepairUpdate(BaseModel):
    """Repair case update model"""
    status: Optional[RepairStatus] = None
    technical_notes: Optional[str] = None
    estimated_completion_date: Optional[datetime] = None
    final_cost: Optional[int] = None


class RepairResponse(BaseModel):
    """Repair case response model"""
    id: int
    client_id: int
    quote_id: int
    status: RepairStatus
    created_at: datetime
    estimated_completion_date: Optional[datetime]
    completed_at: Optional[datetime]
    technical_notes: Optional[str]
    estimated_cost: int
    final_cost: Optional[int]

    class Config:
        from_attributes = True


# Inventory Models

class InventoryItemBase(BaseModel):
    """Base inventory item"""
    name: str = Field(..., min_length=1, max_length=200)
    category: str
    quantity: int = Field(..., ge=0)
    minimum_quantity: int = Field(default=5, ge=0)
    supplier: Optional[str] = None
    unit_cost: int = Field(..., gt=0)
    location: Optional[str] = None


class InventoryItemCreate(InventoryItemBase):
    """Inventory item creation"""
    pass


class InventoryItemResponse(InventoryItemBase):
    """Inventory item response"""
    id: int

    class Config:
        from_attributes = True


# Statistics Models

class StatsResponse(BaseModel):
    """Statistics response"""
    total_repairs: int
    total_revenue: int
    average_repair_cost: int
    completed_repairs: int
    pending_repairs: int
    most_repaired_brands: List[Dict]
    repairs_by_month: List[Dict]
