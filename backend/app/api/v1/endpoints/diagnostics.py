"""
Endpoints para gestión de diagnósticos
"""
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.dependencies import get_current_user, get_current_admin
from backend.app.crud import diagnostic as diagnostic_crud
from backend.app.services import quote_calculator
from backend.app.schemas.diagnostic import (
    DiagnosticCreate,
    DiagnosticUpdate,
    DiagnosticResponse,
    DiagnosticDetail,
    DiagnosticCalculateRequest,
    DiagnosticCalculateResponse,
    FaultBreakdown
)

router = APIRouter(prefix="/diagnostics", tags=["diagnostics"])


@router.post("", response_model=DiagnosticResponse, status_code=status.HTTP_201_CREATED)
async def create_diagnostic(
    diagnostic_in: DiagnosticCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Crear un nuevo diagnóstico

    - Requiere autenticación
    - Solo admin/technician pueden crear diagnósticos
    """
    user_role = current_user.get("role")
    if user_role not in ["admin", "technician"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores y técnicos pueden crear diagnósticos"
        )

    diagnostic = diagnostic_crud.diagnostic.create(db, diagnostic_in)
    return diagnostic


@router.get("", response_model=List[DiagnosticResponse])
async def list_diagnostics(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    Listar todos los diagnósticos

    - Solo admin/technician
    """
    diagnostics = diagnostic_crud.diagnostic.get_all(db, skip=skip, limit=limit)
    return diagnostics


@router.get("/with-quotes", response_model=List[DiagnosticResponse])
async def list_diagnostics_with_quotes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    Listar diagnósticos que tienen cotización

    - Solo admin/technician
    """
    diagnostics = diagnostic_crud.diagnostic.get_with_quotes(db, skip=skip, limit=limit)
    return diagnostics


@router.get("/by-confidence/{min_confidence}", response_model=List[DiagnosticResponse])
async def list_diagnostics_by_confidence(
    min_confidence: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    Listar diagnósticos por confianza mínima de IA

    - Solo admin/technician
    """
    if not 0 <= min_confidence <= 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La confianza debe estar entre 0 y 100"
        )

    diagnostics = diagnostic_crud.diagnostic.get_by_confidence(
        db, min_confidence=min_confidence, skip=skip, limit=limit
    )
    return diagnostics


@router.get("/{diagnostic_id}", response_model=DiagnosticDetail)
async def get_diagnostic(
    diagnostic_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener detalle de un diagnóstico

    - Admin/Technician: puede ver cualquier diagnóstico
    - Client: solo puede ver diagnósticos de sus reparaciones
    """
    diagnostic = diagnostic_crud.diagnostic.get(db, diagnostic_id)
    if not diagnostic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnóstico no encontrado"
        )

    # Verificar permisos si es cliente
    user_role = current_user.get("role")
    if user_role not in ["admin", "technician"]:
        # Cliente solo puede ver diagnósticos de sus reparaciones
        if diagnostic.repair_id:
            from backend.app.crud import repair as repair_crud
            repair = repair_crud.repair.get(db, diagnostic.repair_id)
            if not repair or repair.client_id != int(current_user["user_id"]):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No tienes permiso para ver este diagnóstico"
                )

    return diagnostic


@router.put("/{diagnostic_id}", response_model=DiagnosticDetail)
async def update_diagnostic(
    diagnostic_id: int,
    diagnostic_in: DiagnosticUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    Actualizar un diagnóstico

    - Solo admin/technician
    """
    diagnostic = diagnostic_crud.diagnostic.get(db, diagnostic_id)
    if not diagnostic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnóstico no encontrado"
        )

    diagnostic = diagnostic_crud.diagnostic.update(db, diagnostic, diagnostic_in)
    return diagnostic


@router.post("/{diagnostic_id}/notes", response_model=DiagnosticDetail)
async def add_diagnostic_note(
    diagnostic_id: int,
    note_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    Agregar nota a un diagnóstico

    - Solo admin/technician
    """
    note_text = note_data.get("note")
    if not note_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El campo 'note' es requerido"
        )

    diagnostic = diagnostic_crud.diagnostic.add_note(db, diagnostic_id, note_text)
    if not diagnostic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnóstico no encontrado"
        )

    return diagnostic


@router.post("/calculate", response_model=DiagnosticCalculateResponse)
async def calculate_diagnostic_quote(
    request: DiagnosticCalculateRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Calcular cotización basada en instrumento y fallas

    - Requiere autenticación
    - No persiste en base de datos, solo calcula
    """
    try:
        result = quote_calculator.calculate_quote(
            instrument_id=request.instrument_id,
            brand_id=request.brand_id,
            faults=request.faults
        )

        # Convertir breakdown a schema
        breakdown = [
            FaultBreakdown(
                fault_id=item["fault_id"],
                name=item["name"],
                base_price=item["base_price"],
                severity=item.get("severity")
            )
            for item in result["breakdown"]
        ]

        return DiagnosticCalculateResponse(
            equipment_info=result["equipment_info"],
            faults=result["faults"],
            base_cost=result["base_cost"],
            complexity_factor=result["complexity_multiplier"],
            value_factor=result["value_multiplier"],
            final_cost=result["adjusted_cost"],
            min_price=result["min_price"],
            max_price=result["max_price"],
            breakdown=breakdown,
            labor_hours=result["labor_hours"],
            disclaimer=result["disclaimer"]
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular cotización: {str(e)}"
        )


@router.delete("/{diagnostic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_diagnostic(
    diagnostic_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    Eliminar un diagnóstico

    - Solo admin
    """
    diagnostic = diagnostic_crud.diagnostic.get(db, diagnostic_id)
    if not diagnostic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnóstico no encontrado"
        )

    diagnostic_crud.diagnostic.delete(db, diagnostic_id)
    return None
