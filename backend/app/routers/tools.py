"""
Router Tools - CRUD para herramientas del taller
FASE 1: Implementación aditiva, modelo Tool ya existe
Usa permisos granulares (require_permission).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_admin, require_permission
from app.models.tool import Tool


# =============================================================================
# Schemas
# =============================================================================

class ToolBase(BaseModel):
    name: str
    code: Optional[str] = None
    model: Optional[str] = None
    brand_id: Optional[int] = None
    category_id: Optional[int] = None
    location_id: Optional[int] = None
    serial_number: Optional[str] = None
    specifications: Optional[str] = None
    status: Optional[str] = "available"
    requires_calibration: Optional[int] = 0
    last_calibration_date: Optional[date] = None
    next_calibration_date: Optional[date] = None
    purchase_price: Optional[float] = None
    purchase_date: Optional[date] = None
    warranty_until: Optional[date] = None
    image_url: Optional[str] = None
    manual_url: Optional[str] = None
    notes: Optional[str] = None


class ToolCreate(ToolBase):
    pass


class ToolUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    model: Optional[str] = None
    brand_id: Optional[int] = None
    category_id: Optional[int] = None
    location_id: Optional[int] = None
    serial_number: Optional[str] = None
    specifications: Optional[str] = None
    status: Optional[str] = None
    requires_calibration: Optional[int] = None
    last_calibration_date: Optional[date] = None
    next_calibration_date: Optional[date] = None
    purchase_price: Optional[float] = None
    purchase_date: Optional[date] = None
    warranty_until: Optional[date] = None
    image_url: Optional[str] = None
    manual_url: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[int] = None


class ToolRead(ToolBase):
    id: int
    is_active: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CalibrationRecord(BaseModel):
    calibration_date: date
    next_calibration_date: Optional[date] = None
    notes: Optional[str] = None


# =============================================================================
# Router
# =============================================================================

router = APIRouter(prefix="/tools", tags=["Tools"])


@router.get("/", response_model=List[ToolRead])
def list_tools(
    status: Optional[str] = None,
    requires_calibration: Optional[bool] = None,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("tools", "read")),
):
    """Listar todas las herramientas"""
    query = db.query(Tool).filter(Tool.is_active == 1)

    if status:
        query = query.filter(Tool.status == status)

    if requires_calibration is not None:
        query = query.filter(Tool.requires_calibration == (1 if requires_calibration else 0))

    return query.order_by(Tool.name).all()


@router.get("/{tool_id}", response_model=ToolRead)
def get_tool(
    tool_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("tools", "read")),
):
    """Obtener una herramienta por ID (Admin only)"""
    tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Herramienta {tool_id} no encontrada"
        )
    return tool


@router.post("/", response_model=ToolRead, status_code=status.HTTP_201_CREATED)
def create_tool(
    tool: ToolCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("tools", "create")),
):
    """Crear una nueva herramienta"""
    # Verificar código único si se proporciona
    if tool.code:
        existing = db.query(Tool).filter(Tool.code == tool.code).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe una herramienta con código {tool.code}"
            )

    db_tool = Tool(**tool.model_dump())
    db.add(db_tool)
    db.commit()
    db.refresh(db_tool)
    return db_tool


@router.put("/{tool_id}", response_model=ToolRead)
def update_tool(
    tool_id: int,
    tool: ToolUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("tools", "update")),
):
    """Actualizar una herramienta"""
    db_tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not db_tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Herramienta {tool_id} no encontrada"
        )

    # Verificar código único si se está actualizando
    update_data = tool.model_dump(exclude_unset=True)
    if "code" in update_data and update_data["code"]:
        existing = db.query(Tool).filter(
            Tool.code == update_data["code"],
            Tool.id != tool_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe otra herramienta con código {update_data['code']}"
            )

    for key, value in update_data.items():
        setattr(db_tool, key, value)

    db_tool.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_tool)
    return db_tool


@router.delete("/{tool_id}")
def delete_tool(
    tool_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("tools", "update")),
):
    """Eliminar una herramienta (soft delete) (Admin only)"""
    db_tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not db_tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Herramienta {tool_id} no encontrada"
        )

    # Soft delete
    db_tool.is_active = 0
    db_tool.updated_at = datetime.utcnow()
    db.commit()
    return {"ok": True, "message": f"Herramienta {tool_id} eliminada"}


@router.post("/{tool_id}/calibrate", response_model=ToolRead)
def calibrate_tool(
    tool_id: int,
    calibration: CalibrationRecord,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("tools", "calibrate")),
):
    """Registrar calibración de herramienta"""
    db_tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not db_tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Herramienta {tool_id} no encontrada"
        )

    if not db_tool.requires_calibration:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta herramienta no requiere calibración"
        )

    db_tool.last_calibration_date = calibration.calibration_date
    if calibration.next_calibration_date:
        db_tool.next_calibration_date = calibration.next_calibration_date

    if calibration.notes:
        existing_notes = db_tool.notes or ""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d")
        new_note = f"\n[{timestamp}] Calibración: {calibration.notes}"
        db_tool.notes = existing_notes + new_note

    db_tool.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_tool)
    return db_tool
