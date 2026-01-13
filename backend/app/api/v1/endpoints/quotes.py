"""
Endpoints para gestión de cotizaciones
"""
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.dependencies import get_current_user, get_current_admin
from backend.app.crud import quote as quote_crud
from backend.app.services import quote_calculator
from backend.app.models.quote import QuoteStatus
from backend.app.schemas.quote import (
    QuoteCreate,
    QuoteUpdate,
    QuoteResponse,
    QuoteDetail,
    QuoteEstimateRequest,
    QuoteEstimateResponse
)

router = APIRouter(prefix="/quotes", tags=["quotes"])


@router.post("", response_model=QuoteResponse, status_code=status.HTTP_201_CREATED)
async def create_quote(
    quote_in: QuoteCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    Crear una nueva cotización formal

    - Solo admin/technician
    """
    quote = quote_crud.quote.create(db, quote_in)
    return quote


@router.get("", response_model=List[QuoteResponse])
async def list_quotes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    Listar todas las cotizaciones

    - Solo admin/technician
    """
    quotes = quote_crud.quote.get_all(db, skip=skip, limit=limit)
    return quotes


@router.get("/pending", response_model=List[QuoteResponse])
async def list_pending_quotes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    Listar cotizaciones pendientes

    - Solo admin/technician
    """
    quotes = quote_crud.quote.get_pending(db, skip=skip, limit=limit)
    return quotes


@router.get("/accepted", response_model=List[QuoteResponse])
async def list_accepted_quotes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    Listar cotizaciones aceptadas

    - Solo admin/technician
    """
    quotes = quote_crud.quote.get_accepted(db, skip=skip, limit=limit)
    return quotes


@router.get("/expired", response_model=List[QuoteResponse])
async def list_expired_quotes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    Listar cotizaciones expiradas

    - Solo admin/technician
    """
    quotes = quote_crud.quote.get_expired(db, skip=skip, limit=limit)
    return quotes


@router.get("/by-status/{status}", response_model=List[QuoteResponse])
async def list_quotes_by_status(
    status: QuoteStatus,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    Listar cotizaciones por estado

    - Solo admin/technician
    """
    quotes = quote_crud.quote.get_by_status(db, status=status, skip=skip, limit=limit)
    return quotes


@router.get("/by-diagnostic/{diagnostic_id}", response_model=List[QuoteResponse])
async def list_quotes_by_diagnostic(
    diagnostic_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Listar cotizaciones de un diagnóstico

    - Admin/Technician: puede ver cualquier cotización
    - Client: solo puede ver cotizaciones de sus reparaciones
    """
    user_role = current_user.get("role")

    # Verificar permisos si es cliente
    if user_role not in ["admin", "technician"]:
        from backend.app.crud import diagnostic as diagnostic_crud
        diagnostic = diagnostic_crud.diagnostic.get(db, diagnostic_id)
        if diagnostic and diagnostic.repair_id:
            from backend.app.crud import repair as repair_crud
            repair = repair_crud.repair.get(db, diagnostic.repair_id)
            if not repair or repair.client_id != int(current_user["user_id"]):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No tienes permiso para ver estas cotizaciones"
                )

    quotes = quote_crud.quote.get_by_diagnostic(db, diagnostic_id=diagnostic_id, skip=skip, limit=limit)
    return quotes


@router.get("/by-repair/{repair_id}", response_model=List[QuoteResponse])
async def list_quotes_by_repair(
    repair_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Listar cotizaciones de una reparación

    - Admin/Technician: puede ver cualquier cotización
    - Client: solo puede ver cotizaciones de sus reparaciones
    """
    user_role = current_user.get("role")

    # Verificar permisos si es cliente
    if user_role not in ["admin", "technician"]:
        from backend.app.crud import repair as repair_crud
        repair = repair_crud.repair.get(db, repair_id)
        if not repair or repair.client_id != int(current_user["user_id"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para ver estas cotizaciones"
            )

    quotes = quote_crud.quote.get_by_repair(db, repair_id=repair_id, skip=skip, limit=limit)
    return quotes


@router.get("/stats", response_model=dict)
async def get_quote_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    Obtener estadísticas de cotizaciones

    - Solo admin
    """
    stats = quote_crud.quote.get_stats(db)
    return stats


@router.get("/{quote_id}", response_model=QuoteDetail)
async def get_quote(
    quote_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener detalle de una cotización

    - Admin/Technician: puede ver cualquier cotización
    - Client: solo puede ver cotizaciones de sus reparaciones
    """
    quote = quote_crud.quote.get(db, quote_id)
    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cotización no encontrada"
        )

    # Verificar permisos si es cliente
    user_role = current_user.get("role")
    if user_role not in ["admin", "technician"]:
        if quote.repair_id:
            from backend.app.crud import repair as repair_crud
            repair = repair_crud.repair.get(db, quote.repair_id)
            if not repair or repair.client_id != int(current_user["user_id"]):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No tienes permiso para ver esta cotización"
                )

    return quote


@router.put("/{quote_id}", response_model=QuoteDetail)
async def update_quote(
    quote_id: int,
    quote_in: QuoteUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    Actualizar una cotización

    - Solo admin/technician
    """
    quote = quote_crud.quote.get(db, quote_id)
    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cotización no encontrada"
        )

    quote = quote_crud.quote.update(db, quote, quote_in)
    return quote


@router.patch("/{quote_id}/status", response_model=QuoteResponse)
async def update_quote_status(
    quote_id: int,
    status_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Actualizar estado de cotización

    - Admin/Technician: puede cambiar a cualquier estado
    - Client: solo puede aceptar o rechazar
    """
    new_status_str = status_data.get("status")
    notes = status_data.get("notes")

    if not new_status_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El campo 'status' es requerido"
        )

    try:
        new_status = QuoteStatus(new_status_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado inválido. Estados disponibles: {[s.value for s in QuoteStatus]}"
        )

    quote = quote_crud.quote.get(db, quote_id)
    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cotización no encontrada"
        )

    # Verificar permisos
    user_role = current_user.get("role")
    if user_role not in ["admin", "technician"]:
        # Cliente solo puede aceptar o rechazar
        if new_status not in [QuoteStatus.ACCEPTED, QuoteStatus.REJECTED]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo puedes aceptar o rechazar cotizaciones"
            )

        # Verificar que sea su cotización
        if quote.repair_id:
            from backend.app.crud import repair as repair_crud
            repair = repair_crud.repair.get(db, quote.repair_id)
            if not repair or repair.client_id != int(current_user["user_id"]):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No tienes permiso para modificar esta cotización"
                )

    quote = quote_crud.quote.update_status(db, quote_id, new_status, notes)
    return quote


@router.post("/estimate", response_model=QuoteEstimateResponse)
async def estimate_quote(
    request: QuoteEstimateRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Estimar cotización sin persistir

    - Requiere autenticación
    - No guarda en base de datos, solo calcula
    """
    try:
        result = quote_calculator.calculate_quote(
            instrument_id=request.instrument_id,
            brand_id=request.brand_id,
            faults=request.faults
        )

        return QuoteEstimateResponse(
            instrument_brand=result["equipment_info"]["brand"],
            instrument_model=result["equipment_info"]["model"],
            instrument_tier=result["equipment_info"]["tier"],
            instrument_value_avg=result["equipment_info"]["value"],
            faults=result["faults"],
            base_total=result["base_cost"],
            complexity_multiplier=result["complexity_multiplier"],
            value_multiplier=result["value_multiplier"],
            adjusted_total=result["adjusted_cost"],
            min_price=result["min_price"],
            max_price=result["max_price"],
            labor_hours=result["labor_hours"],
            breakdown=result["breakdown"],
            max_recommended=result["max_recommended"],
            exceeds_recommendation=result["exceeds_recommendation"],
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
            detail=f"Error al estimar cotización: {str(e)}"
        )


@router.delete("/{quote_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quote(
    quote_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    Eliminar una cotización

    - Solo admin
    """
    quote = quote_crud.quote.get(db, quote_id)
    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cotización no encontrada"
        )

    quote_crud.quote.delete(db, quote_id)
    return None
