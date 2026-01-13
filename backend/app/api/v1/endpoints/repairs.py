"""
Endpoints para gestión de reparaciones
"""
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.dependencies import get_current_user, get_current_admin
from backend.app.crud import repair as repair_crud
from backend.app.models.repair import RepairStatus
from backend.app.schemas.repair import (
    RepairCreate,
    RepairUpdate,
    RepairResponse,
    RepairDetail,
    RepairStatusUpdate,
    RepairNoteCreate,
    RepairStats
)

router = APIRouter(prefix="/repairs", tags=["repairs"])


@router.post("", response_model=RepairResponse, status_code=status.HTTP_201_CREATED)
async def create_repair(
    repair_in: RepairCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Crear una nueva reparación

    - Requiere autenticación
    - El client_id en el body debe coincidir con el usuario actual (excepto admin)
    """
    # Verificar permisos: solo admin puede crear reparaciones para otros clientes
    if current_user.get("role") != "admin":
        if repair_in.client_id != int(current_user["user_id"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No puedes crear reparaciones para otros clientes"
            )

    repair = repair_crud.repair.create(db, repair_in)
    return repair


@router.get("", response_model=List[RepairResponse])
async def list_repairs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Listar reparaciones

    - Admin/Technician: ve todas las reparaciones
    - Client: solo ve sus propias reparaciones
    """
    user_role = current_user.get("role")
    user_id = int(current_user["user_id"])

    if user_role in ["admin", "technician"]:
        # Admin y técnicos ven todas las reparaciones
        repairs = repair_crud.repair.get_all(db, skip=skip, limit=limit)
    else:
        # Clientes solo ven sus reparaciones
        repairs = repair_crud.repair.get_by_client(db, client_id=user_id, skip=skip, limit=limit)

    return repairs


@router.get("/active", response_model=List[RepairResponse])
async def list_active_repairs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Listar reparaciones activas (no canceladas ni entregadas)

    - Admin/Technician: ve todas las reparaciones activas
    - Client: solo ve sus propias reparaciones activas
    """
    user_role = current_user.get("role")
    user_id = int(current_user["user_id"])

    active_repairs = repair_crud.repair.get_active(db, skip=skip, limit=limit)

    # Filtrar por cliente si no es admin/technician
    if user_role not in ["admin", "technician"]:
        active_repairs = [r for r in active_repairs if r.client_id == user_id]

    return active_repairs


@router.get("/stats", response_model=RepairStats)
async def get_repair_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    Obtener estadísticas de reparaciones

    - Solo admin
    """
    stats = repair_crud.repair.get_stats(db)
    return stats


@router.get("/by-status/{status}", response_model=List[RepairResponse])
async def list_repairs_by_status(
    status: RepairStatus,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    Listar reparaciones por estado

    - Solo admin/technician
    """
    repairs = repair_crud.repair.get_by_status(db, status=status, skip=skip, limit=limit)
    return repairs


@router.get("/by-client/{client_id}", response_model=List[RepairResponse])
async def list_repairs_by_client(
    client_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Listar reparaciones de un cliente específico

    - Admin: puede ver cualquier cliente
    - Client: solo puede ver sus propias reparaciones
    """
    user_role = current_user.get("role")
    user_id = int(current_user["user_id"])

    # Verificar permisos
    if user_role != "admin" and client_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver reparaciones de otros clientes"
        )

    repairs = repair_crud.repair.get_by_client(db, client_id=client_id, skip=skip, limit=limit)
    return repairs


@router.get("/{repair_id}", response_model=RepairDetail)
async def get_repair(
    repair_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener detalle de una reparación

    - Admin/Technician: puede ver cualquier reparación
    - Client: solo puede ver sus propias reparaciones
    """
    repair = repair_crud.repair.get(db, repair_id)
    if not repair:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reparación no encontrada"
        )

    # Verificar permisos
    user_role = current_user.get("role")
    user_id = int(current_user["user_id"])

    if user_role not in ["admin", "technician"] and repair.client_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver esta reparación"
        )

    return repair


@router.put("/{repair_id}", response_model=RepairDetail)
async def update_repair(
    repair_id: int,
    repair_in: RepairUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    Actualizar una reparación

    - Solo admin/technician
    """
    repair = repair_crud.repair.get(db, repair_id)
    if not repair:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reparación no encontrada"
        )

    repair = repair_crud.repair.update(db, repair, repair_in)
    return repair


@router.patch("/{repair_id}/status", response_model=RepairDetail)
async def update_repair_status(
    repair_id: int,
    status_update: RepairStatusUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    Actualizar estado de una reparación

    - Solo admin/technician
    - Actualiza timestamps automáticamente según el estado
    """
    repair = repair_crud.repair.update_status(
        db,
        repair_id=repair_id,
        new_status=status_update.status,
        notes=status_update.notes
    )

    if not repair:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reparación no encontrada"
        )

    return repair


@router.post("/{repair_id}/notes", response_model=RepairDetail)
async def add_repair_note(
    repair_id: int,
    note_in: RepairNoteCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    Agregar nota a una reparación

    - Solo admin/technician
    - Las notas incluyen timestamp automático
    """
    repair = repair_crud.repair.add_note(
        db,
        repair_id=repair_id,
        note_text=note_in.note
    )

    if not repair:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reparación no encontrada"
        )

    return repair


@router.delete("/{repair_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_repair(
    repair_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    Eliminar una reparación

    - Solo admin
    - Eliminación permanente (hard delete)
    """
    repair = repair_crud.repair.get(db, repair_id)
    if not repair:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reparación no encontrada"
        )

    repair_crud.repair.delete(db, repair_id)
    return None
