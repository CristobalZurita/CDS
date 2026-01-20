"""
Router de Garantías
===================
Endpoints para gestión de garantías y reclamos.
ADITIVO: Nuevo router, no modifica existentes.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_admin
from app.services.warranty_service import WarrantyService
from app.models.warranty import WarrantyType, WarrantyStatus, ClaimStatus

router = APIRouter(prefix="/warranties", tags=["Warranties"])


# ============================================================================
# CRUD DE GARANTÍAS
# ============================================================================

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_warranty(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Crear garantía para una reparación.

    Body:
    - repair_id: ID de la reparación (requerido)
    - warranty_type: Tipo (labor, parts, full, limited, extended)
    - duration_days: Duración en días (usa default si no se especifica)
    - coverage_description: Descripción de cobertura
    - exclusions: Exclusiones
    - max_claim_amount: Monto máximo de reclamo
    - max_claims: Número máximo de reclamos
    """
    svc = WarrantyService(db)
    user_id = int(user.get("user_id")) if user and user.get("user_id") else None

    if "repair_id" not in payload:
        raise HTTPException(status_code=400, detail="repair_id requerido")

    warranty = svc.create_warranty(
        repair_id=payload["repair_id"],
        warranty_type=payload.get("warranty_type", WarrantyType.FULL.value),
        duration_days=payload.get("duration_days"),
        coverage_description=payload.get("coverage_description"),
        exclusions=payload.get("exclusions"),
        max_claim_amount=payload.get("max_claim_amount"),
        max_claims=payload.get("max_claims", 1),
        created_by=user_id
    )

    return warranty


@router.post("/auto-create/{repair_id}", status_code=status.HTTP_201_CREATED)
def auto_create_warranty(
    repair_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Crear garantía automáticamente para reparación completada"""
    svc = WarrantyService(db)
    user_id = int(user.get("user_id")) if user and user.get("user_id") else None

    return svc.create_for_completed_repair(repair_id, created_by=user_id)


@router.get("/")
def list_warranties(
    client_id: Optional[int] = None,
    status: Optional[str] = None,
    expiring_in_days: Optional[int] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Listar garantías con filtros.

    Query params:
    - client_id: Filtrar por cliente
    - status: Filtrar por estado (active, expired, voided, etc.)
    - expiring_in_days: Garantías que expiran en N días
    """
    svc = WarrantyService(db)

    return svc.list_warranties(
        client_id=client_id,
        status=status,
        expiring_in_days=expiring_in_days,
        limit=limit,
        offset=offset
    )


@router.get("/expiring-soon")
def get_expiring_soon(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Obtener garantías que expiran pronto"""
    svc = WarrantyService(db)
    return svc.get_expiring_soon(days=days)


@router.get("/by-repair/{repair_id}")
def get_warranty_by_repair(
    repair_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Obtener garantía de una reparación"""
    svc = WarrantyService(db)
    warranty = svc.get_warranty_by_repair(repair_id)
    if not warranty:
        raise HTTPException(status_code=404, detail="No se encontró garantía para esta reparación")
    return warranty


@router.get("/check-coverage/{repair_id}")
def check_warranty_coverage(
    repair_id: int,
    problem_description: Optional[str] = None,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Verificar cobertura de garantía.

    Retorna información sobre si la reparación tiene garantía vigente
    y si un nuevo problema estaría cubierto.
    """
    svc = WarrantyService(db)
    return svc.check_coverage(repair_id, problem_description)


@router.get("/{warranty_id}")
def get_warranty(
    warranty_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Obtener detalle de garantía"""
    svc = WarrantyService(db)
    return svc.get_warranty(warranty_id)


@router.post("/{warranty_id}/void")
def void_warranty(
    warranty_id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_admin)
):
    """Anular garantía (solo admin)"""
    svc = WarrantyService(db)
    user_id = int(user.get("user_id")) if user and user.get("user_id") else None

    reason = payload.get("reason")
    if not reason:
        raise HTTPException(status_code=400, detail="Razón de anulación requerida")

    warranty = svc.void_warranty(warranty_id, reason=reason, voided_by=user_id)
    return {"ok": True, "warranty": warranty}


# ============================================================================
# RECLAMOS DE GARANTÍA
# ============================================================================

@router.post("/{warranty_id}/claims", status_code=status.HTTP_201_CREATED)
def submit_claim(
    warranty_id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Presentar reclamo de garantía.

    Body:
    - problem_description: Descripción del problema (requerido)
    - fault_type: Tipo de falla (opcional)
    """
    svc = WarrantyService(db)
    user_id = int(user.get("user_id")) if user and user.get("user_id") else None

    problem = payload.get("problem_description")
    if not problem:
        raise HTTPException(status_code=400, detail="Descripción del problema requerida")

    claim = svc.submit_claim(
        warranty_id=warranty_id,
        problem_description=problem,
        fault_type=payload.get("fault_type"),
        submitted_by=user_id
    )

    return claim


@router.get("/claims")
def list_all_claims(
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Listar todos los reclamos"""
    svc = WarrantyService(db)
    return svc.list_claims(status=status, limit=limit, offset=offset)


@router.get("/{warranty_id}/claims")
def list_warranty_claims(
    warranty_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Listar reclamos de una garantía"""
    svc = WarrantyService(db)
    return svc.list_claims(warranty_id=warranty_id)


@router.get("/claims/{claim_id}")
def get_claim(
    claim_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Obtener detalle de reclamo"""
    svc = WarrantyService(db)
    return svc.get_claim(claim_id)


@router.post("/claims/{claim_id}/evaluate")
def evaluate_claim(
    claim_id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_admin)
):
    """
    Evaluar reclamo de garantía (solo admin).

    Body:
    - is_covered: ¿Está cubierto? (requerido)
    - evaluation_notes: Notas de evaluación
    - rejection_reason: Razón de rechazo (si is_covered=false)
    - estimated_cost: Costo estimado de reparación
    """
    svc = WarrantyService(db)
    user_id = int(user.get("user_id")) if user and user.get("user_id") else None

    if "is_covered" not in payload:
        raise HTTPException(status_code=400, detail="is_covered requerido")

    claim = svc.evaluate_claim(
        claim_id=claim_id,
        is_covered=payload["is_covered"],
        evaluation_notes=payload.get("evaluation_notes"),
        rejection_reason=payload.get("rejection_reason"),
        estimated_cost=payload.get("estimated_cost", 0),
        evaluated_by=user_id
    )

    return {"ok": True, "claim": claim}


@router.post("/claims/{claim_id}/process")
def process_claim(
    claim_id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Procesar reclamo aprobado (iniciar reparación).

    Body:
    - new_repair_id: ID de la nueva reparación (opcional)
    - actual_cost: Costo real
    - customer_copay: Copago del cliente
    """
    svc = WarrantyService(db)

    claim = svc.process_claim(
        claim_id=claim_id,
        new_repair_id=payload.get("new_repair_id"),
        actual_cost=payload.get("actual_cost", 0),
        customer_copay=payload.get("customer_copay", 0)
    )

    return {"ok": True, "claim": claim}


@router.post("/claims/{claim_id}/complete")
def complete_claim(
    claim_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Completar reclamo (reparación finalizada)"""
    svc = WarrantyService(db)
    claim = svc.complete_claim(claim_id)
    return {"ok": True, "claim": claim}


# ============================================================================
# MANTENIMIENTO
# ============================================================================

@router.post("/maintenance/update-expired")
def update_expired_warranties(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_admin)
):
    """Actualizar garantías expiradas (job de mantenimiento)"""
    svc = WarrantyService(db)
    count = svc.update_expired_warranties()
    return {"ok": True, "updated": count}
