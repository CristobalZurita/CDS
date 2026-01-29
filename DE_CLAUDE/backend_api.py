"""
Backend API for Interactive Instrument Diagnostic System
FastAPI + SQLAlchemy + OpenCV for image processing
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, JSON, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker, relationship
from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import cv2
import numpy as np
from pathlib import Path
import base64
from io import BytesIO
from PIL import Image
import uuid

# Database setup
DATABASE_URL = "sqlite:///./diagnostic_system.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class InstrumentModel(Base):
    """Instrument catalog with predefined templates"""
    __tablename__ = "instruments"
    
    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, nullable=False, index=True)
    model = Column(String, nullable=False)
    year = Column(Integer, nullable=True)
    type = Column(String, nullable=True)  # Synth, Drum Machine, etc.
    estimated_value = Column(Float, nullable=True)
    complexity_tier = Column(String, default="standard")  # simple, standard, complex, vintage
    
    # Reference photos
    front_photo_url = Column(String, nullable=True)
    back_photo_url = Column(String, nullable=True)
    top_photo_url = Column(String, nullable=True)
    
    # Component template (JSON)
    template_json = Column(JSON, nullable=True)
    
    # Relationships
    photos = relationship("InstrumentPhoto", back_populates="instrument")
    diagnostics = relationship("Diagnostic", back_populates="instrument")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class InstrumentPhoto(Base):
    """Reference photos for instruments with control mapping"""
    __tablename__ = "instrument_photos"
    
    id = Column(Integer, primary_key=True, index=True)
    instrument_id = Column(Integer, ForeignKey("instruments.id"))
    view_type = Column(String, nullable=False)  # front, back, top, detail
    photo_url = Column(String, nullable=False)
    
    # Control detection data (JSON)
    # {
    #   "controls": [
    #     {"id": "knob_1", "type": "knob", "x": 120, "y": 80, "label": "Filter Cutoff"},
    #     {"id": "key_1", "type": "key", "x": 50, "y": 200, "label": "C3"}
    #   ]
    # }
    control_map = Column(JSON, nullable=True)
    
    # Image processing metadata
    width = Column(Integer)
    height = Column(Integer)
    
    instrument = relationship("InstrumentModel", back_populates="photos")
    created_at = Column(DateTime, default=datetime.utcnow)


class Diagnostic(Base):
    """Customer diagnostic submissions"""
    __tablename__ = "diagnostics"
    
    id = Column(Integer, primary_key=True, index=True)
    reference_code = Column(String, unique=True, index=True, nullable=False)
    
    # Customer info
    customer_name = Column(String, nullable=True)
    customer_email = Column(String, nullable=True)
    customer_phone = Column(String, nullable=True)
    
    # Instrument info
    instrument_id = Column(Integer, ForeignKey("instruments.id"), nullable=True)
    custom_instrument_description = Column(String, nullable=True)
    
    # Selected components (JSON array of component IDs)
    selected_components = Column(JSON, nullable=False)
    
    # Status
    status = Column(String, default="pending")  # pending, reviewed, quoted, approved, completed
    
    # Relationships
    instrument = relationship("InstrumentModel", back_populates="diagnostics")
    photos = relationship("DiagnosticPhoto", back_populates="diagnostic")
    quote = relationship("Quote", back_populates="diagnostic", uselist=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DiagnosticPhoto(Base):
    """Photos uploaded by customer with fault markers"""
    __tablename__ = "diagnostic_photos"
    
    id = Column(Integer, primary_key=True, index=True)
    diagnostic_id = Column(Integer, ForeignKey("diagnostics.id"))
    view_type = Column(String, nullable=False)
    photo_url = Column(String, nullable=False)
    
    # Fault markers (JSON)
    # [
    #   {"x": 120, "y": 80, "type": "broken", "component": "knob_1"},
    #   {"x": 150, "y": 100, "type": "missing", "component": "button_2"}
    # ]
    markers = Column(JSON, nullable=True)
    
    diagnostic = relationship("Diagnostic", back_populates="photos")
    created_at = Column(DateTime, default=datetime.utcnow)


class Quote(Base):
    """Generated quotation for diagnostic"""
    __tablename__ = "quotes"
    
    id = Column(Integer, primary_key=True, index=True)
    diagnostic_id = Column(Integer, ForeignKey("diagnostics.id"), unique=True)
    
    # Pricing
    base_diagnostic_fee = Column(Float, default=25000)
    repair_cost = Column(Float, nullable=False)
    complexity_adjustment = Column(Float, default=0)
    parts_cost = Column(Float, default=0)
    subtotal = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    
    # Time estimate
    estimated_days = Column(Integer, default=5)
    
    # Breakdown (JSON)
    cost_breakdown = Column(JSON, nullable=True)
    
    # Approval
    approved_by_customer = Column(Boolean, default=False)
    approved_at = Column(DateTime, nullable=True)
    
    diagnostic = relationship("Diagnostic", back_populates="quote")
    created_at = Column(DateTime, default=datetime.utcnow)


# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic schemas
class ComponentQuantity(BaseModel):
    component_id: str
    quantity: int = 1


class FaultMarker(BaseModel):
    x: float
    y: float
    actual_x: float
    actual_y: float
    type: str
    timestamp: int
    component: Optional[str] = None


class PhotoSubmission(BaseModel):
    view: str
    markers: List[FaultMarker]
    base64_image: str


class DiagnosticSubmission(BaseModel):
    instrument_id: Optional[int] = None
    custom_instrument_description: Optional[str] = None
    selected_components: List[str]
    component_quantities: Dict[str, int] = {}
    photos: List[PhotoSubmission]
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None


class QuoteCalculation(BaseModel):
    base_diagnostic: float
    repair_cost: float
    complexity_factor: float
    complexity_adjustment: float
    parts_cost: float
    subtotal: float
    total: float
    estimated_days: int
    breakdown: List[Dict[str, Any]]


class InstrumentResponse(BaseModel):
    id: int
    brand: str
    model: str
    year: Optional[int]
    type: Optional[str]
    estimated_value: Optional[float]
    front_photo_url: Optional[str]
    template_json: Optional[Dict]
    
    class Config:
        orm_mode = True


# FastAPI app
app = FastAPI(title="Instrument Diagnostic API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Pricing configuration
FAULT_BASE_PRICES = {
    "broken": 15000,
    "missing": 20000,
    "loose": 8000,
    "noisy": 12000,
    "stuck": 10000,
    "oxidized": 18000,
}

COMPONENT_DIFFICULTY = {
    "keys": 1.5,
    "keybed": 2.0,
    "knobs": 1.0,
    "sliders": 1.2,
    "buttons": 0.8,
    "switches": 0.9,
    "audio_out": 1.3,
    "audio_in": 1.3,
    "midi": 1.1,
    "cv_gate": 1.4,
    "display": 2.5,
    "power": 2.0,
}

COMPLEXITY_TIERS = {
    "simple": 1.0,
    "standard": 1.2,
    "complex": 1.5,
    "vintage": 2.0,
}


# Helper functions
def generate_reference_code() -> str:
    """Generate unique reference code"""
    return f"DIAG-{uuid.uuid4().hex[:8].upper()}"


def save_uploaded_image(base64_data: str, directory: str = "uploads") -> str:
    """Save base64 image to disk and return URL"""
    Path(directory).mkdir(exist_ok=True)
    
    # Remove data URL prefix if present
    if "," in base64_data:
        base64_data = base64_data.split(",")[1]
    
    # Decode and save
    image_data = base64.b64decode(base64_data)
    image = Image.open(BytesIO(image_data))
    
    filename = f"{uuid.uuid4().hex}.jpg"
    filepath = Path(directory) / filename
    image.save(filepath, "JPEG", quality=90)
    
    return f"/{directory}/{filename}"


def detect_controls_opencv(image_array: np.ndarray) -> List[Dict]:
    """
    Use OpenCV to detect potential controls in instrument photo
    This is a simplified version - real implementation would be more sophisticated
    """
    controls = []
    
    # Convert to grayscale
    gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
    
    # Detect circles (knobs/buttons)
    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=30,
        param1=50,
        param2=30,
        minRadius=10,
        maxRadius=50
    )
    
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i, circle in enumerate(circles[0, :]):
            x, y, r = circle
            controls.append({
                "id": f"detected_knob_{i}",
                "type": "knob",
                "x": int(x),
                "y": int(y),
                "radius": int(r),
                "confidence": 0.7
            })
    
    # Detect rectangles (sliders/buttons)
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for i, contour in enumerate(contours):
        if cv2.contourArea(contour) > 100:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = float(w) / h if h > 0 else 0
            
            # Detect sliders (long rectangles)
            if 2 < aspect_ratio < 10 or 0.1 < aspect_ratio < 0.5:
                controls.append({
                    "id": f"detected_slider_{i}",
                    "type": "slider",
                    "x": int(x + w/2),
                    "y": int(y + h/2),
                    "width": int(w),
                    "height": int(h),
                    "confidence": 0.6
                })
    
    return controls


def calculate_quote(
    instrument: Optional[InstrumentModel],
    markers: List[FaultMarker],
    selected_components: List[str],
    component_quantities: Dict[str, int]
) -> QuoteCalculation:
    """Calculate detailed quotation based on diagnostic data"""
    
    base_diagnostic = 25000
    repair_cost = 0
    breakdown = []
    
    # Calculate cost per fault type
    fault_counts = {}
    for marker in markers:
        fault_type = marker.type
        fault_counts[fault_type] = fault_counts.get(fault_type, 0) + 1
        repair_cost += FAULT_BASE_PRICES.get(fault_type, 10000)
        
        breakdown.append({
            "description": f"Reparación: {fault_type}",
            "type": fault_type,
            "cost": FAULT_BASE_PRICES.get(fault_type, 10000)
        })
    
    # Complexity factor based on instrument tier
    complexity_tier = instrument.complexity_tier if instrument else "standard"
    base_complexity = COMPLEXITY_TIERS.get(complexity_tier, 1.2)
    
    # Additional complexity based on components
    component_complexity = 0
    for comp_id in selected_components:
        difficulty = COMPONENT_DIFFICULTY.get(comp_id, 1.0)
        quantity = component_quantities.get(comp_id, 1)
        component_complexity += (difficulty - 1.0) * quantity * 0.1
    
    complexity_factor = base_complexity + component_complexity
    complexity_adjustment = repair_cost * (complexity_factor - 1.0)
    
    # Estimate parts cost (simplified)
    parts_cost = fault_counts.get("missing", 0) * 15000
    
    subtotal = base_diagnostic + repair_cost + complexity_adjustment + parts_cost
    total = round(subtotal)
    
    # Estimate days
    estimated_days = max(3, min(15, len(markers) + len(selected_components) // 5))
    
    return QuoteCalculation(
        base_diagnostic=base_diagnostic,
        repair_cost=repair_cost,
        complexity_factor=round(complexity_factor, 2),
        complexity_adjustment=complexity_adjustment,
        parts_cost=parts_cost,
        subtotal=subtotal,
        total=total,
        estimated_days=estimated_days,
        breakdown=breakdown
    )


# API Endpoints

@app.get("/")
def read_root():
    return {"message": "Instrument Diagnostic API", "version": "1.0.0"}


@app.get("/api/instruments", response_model=List[InstrumentResponse])
def get_instruments(
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of instruments from catalog"""
    query = db.query(InstrumentModel)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (InstrumentModel.brand.ilike(search_term)) |
            (InstrumentModel.model.ilike(search_term))
        )
    
    instruments = query.all()
    return instruments


@app.get("/api/instruments/{instrument_id}", response_model=InstrumentResponse)
def get_instrument(instrument_id: int, db: Session = Depends(get_db)):
    """Get specific instrument with template"""
    instrument = db.query(InstrumentModel).filter(
        InstrumentModel.id == instrument_id
    ).first()
    
    if not instrument:
        raise HTTPException(status_code=404, detail="Instrument not found")
    
    return instrument


@app.post("/api/instruments/{instrument_id}/detect-controls")
async def detect_controls(
    instrument_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a photo and get AI-detected controls
    Used by technician to help build templates
    """
    instrument = db.query(InstrumentModel).filter(
        InstrumentModel.id == instrument_id
    ).first()
    
    if not instrument:
        raise HTTPException(status_code=404, detail="Instrument not found")
    
    # Read and process image
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Detect controls
    controls = detect_controls_opencv(image)
    
    return {
        "instrument_id": instrument_id,
        "detected_controls": controls,
        "count": len(controls)
    }


@app.post("/api/diagnostics/submit")
def submit_diagnostic(
    submission: DiagnosticSubmission,
    db: Session = Depends(get_db)
):
    """Submit complete diagnostic with photos and markers"""
    
    # Generate reference code
    reference_code = generate_reference_code()
    
    # Create diagnostic
    diagnostic = Diagnostic(
        reference_code=reference_code,
        instrument_id=submission.instrument_id,
        custom_instrument_description=submission.custom_instrument_description,
        selected_components=submission.selected_components,
        customer_name=submission.customer_name,
        customer_email=submission.customer_email,
        customer_phone=submission.customer_phone,
        status="pending"
    )
    db.add(diagnostic)
    db.flush()
    
    # Save photos and markers
    all_markers = []
    for photo_data in submission.photos:
        photo_url = save_uploaded_image(photo_data.base64_image)
        
        diagnostic_photo = DiagnosticPhoto(
            diagnostic_id=diagnostic.id,
            view_type=photo_data.view,
            photo_url=photo_url,
            markers=[marker.dict() for marker in photo_data.markers]
        )
        db.add(diagnostic_photo)
        
        all_markers.extend(photo_data.markers)
    
    # Get instrument if selected
    instrument = None
    if submission.instrument_id:
        instrument = db.query(InstrumentModel).filter(
            InstrumentModel.id == submission.instrument_id
        ).first()
    
    # Calculate quote
    quote_calc = calculate_quote(
        instrument,
        all_markers,
        submission.selected_components,
        submission.component_quantities
    )
    
    # Save quote
    quote = Quote(
        diagnostic_id=diagnostic.id,
        base_diagnostic_fee=quote_calc.base_diagnostic,
        repair_cost=quote_calc.repair_cost,
        complexity_adjustment=quote_calc.complexity_adjustment,
        parts_cost=quote_calc.parts_cost,
        subtotal=quote_calc.subtotal,
        total=quote_calc.total,
        estimated_days=quote_calc.estimated_days,
        cost_breakdown=quote_calc.breakdown
    )
    db.add(quote)
    
    db.commit()
    
    return {
        "success": True,
        "reference_code": reference_code,
        "diagnostic_id": diagnostic.id,
        "quote": quote_calc.dict()
    }


@app.get("/api/diagnostics/{reference_code}")
def get_diagnostic(reference_code: str, db: Session = Depends(get_db)):
    """Get diagnostic by reference code"""
    diagnostic = db.query(Diagnostic).filter(
        Diagnostic.reference_code == reference_code
    ).first()
    
    if not diagnostic:
        raise HTTPException(status_code=404, detail="Diagnostic not found")
    
    return {
        "reference_code": diagnostic.reference_code,
        "status": diagnostic.status,
        "instrument": diagnostic.instrument,
        "photos": diagnostic.photos,
        "quote": diagnostic.quote,
        "created_at": diagnostic.created_at
    }


@app.post("/api/quotes/{quote_id}/approve")
def approve_quote(quote_id: int, db: Session = Depends(get_db)):
    """Customer approves quote"""
    quote = db.query(Quote).filter(Quote.id == quote_id).first()
    
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    quote.approved_by_customer = True
    quote.approved_at = datetime.utcnow()
    
    # Update diagnostic status
    diagnostic = quote.diagnostic
    diagnostic.status = "approved"
    
    db.commit()
    
    return {"success": True, "message": "Quote approved"}


# Seed database with sample instruments
@app.post("/api/admin/seed-database")
def seed_database(db: Session = Depends(get_db)):
    """Seed database with sample instruments (admin only)"""
    
    sample_instruments = [
        {
            "brand": "Moog",
            "model": "Minimoog Model D",
            "year": 1970,
            "type": "Analog Synthesizer",
            "estimated_value": 5000000,
            "complexity_tier": "vintage",
            "template_json": {
                "keys": 44,
                "knobs": 24,
                "switches": 18,
                "wheels": 2
            }
        },
        {
            "brand": "Roland",
            "model": "Jupiter-8",
            "year": 1981,
            "type": "Analog Synthesizer",
            "estimated_value": 8000000,
            "complexity_tier": "vintage",
            "template_json": {
                "keys": 61,
                "knobs": 36,
                "buttons": 24,
                "sliders": 8
            }
        },
        {
            "brand": "Korg",
            "model": "MS-20",
            "year": 1978,
            "type": "Semi-Modular Synthesizer",
            "estimated_value": 1500000,
            "complexity_tier": "complex",
            "template_json": {
                "keys": 37,
                "knobs": 19,
                "switches": 6,
                "cv_gate": 12
            }
        },
        {
            "brand": "Yamaha",
            "model": "DX7",
            "year": 1983,
            "type": "Digital Synthesizer",
            "estimated_value": 800000,
            "complexity_tier": "standard",
            "template_json": {
                "keys": 61,
                "buttons": 32,
                "display": 1,
                "sliders": 2
            }
        }
    ]
    
    for inst_data in sample_instruments:
        existing = db.query(InstrumentModel).filter(
            InstrumentModel.brand == inst_data["brand"],
            InstrumentModel.model == inst_data["model"]
        ).first()
        
        if not existing:
            instrument = InstrumentModel(**inst_data)
            db.add(instrument)
    
    db.commit()
    
    return {"success": True, "message": "Database seeded"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
