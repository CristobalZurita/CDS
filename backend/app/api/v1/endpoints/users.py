"""
Endpoints para gestión de usuarios (admin)
Nota: Los endpoints de auth (login, register, /me) están en auth.py
"""
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.dependencies import get_current_user, get_current_admin
from backend.app.crud import user as user_crud
from backend.app.models.user import UserRole
from backend.app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserDetailResponse
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    Listar todos los usuarios

    - Solo admin
    """
    users = user_crud.user.get_all(db, skip=skip, limit=limit)
    return users


@router.get("/active", response_model=List[UserResponse])
async def list_active_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    Listar usuarios activos

    - Solo admin
    """
    users = user_crud.user.get_active_users(db, skip=skip, limit=limit)
    return users


@router.get("/by-role/{role}", response_model=List[UserResponse])
async def list_users_by_role(
    role: UserRole,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    Listar usuarios por rol

    - Solo admin
    - Roles disponibles: client, technician, admin
    """
    users = user_crud.user.get_by_role(db, role=role, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=UserDetailResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener detalle de un usuario

    - Admin: puede ver cualquier usuario
    - Usuario: solo puede ver su propio perfil
    """
    user = user_crud.user.get(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    # Verificar permisos
    current_user_id = int(current_user["user_id"])
    user_role = current_user.get("role")

    if user_role != "admin" and user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver este usuario"
        )

    return user


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    Crear un nuevo usuario

    - Solo admin
    - Nota: Los usuarios normales se registran vía /auth/register
    """
    # Verificar si el email ya existe
    existing_email = user_crud.user.get_by_email(db, user_in.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email ya registrado"
        )

    # Verificar si el username ya existe
    existing_username = user_crud.user.get_by_username(db, user_in.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username ya existe"
        )

    user = user_crud.user.create(db, user_in)
    return user


@router.put("/{user_id}", response_model=UserDetailResponse)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Actualizar información de un usuario

    - Admin: puede actualizar cualquier usuario
    - Usuario: solo puede actualizar su propio perfil
    """
    user = user_crud.user.get(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    # Verificar permisos
    current_user_id = int(current_user["user_id"])
    user_role = current_user.get("role")

    if user_role != "admin" and user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para actualizar este usuario"
        )

    user = user_crud.user.update(db, user, user_in)
    return user


@router.patch("/{user_id}/password", response_model=UserResponse)
async def update_user_password(
    user_id: int,
    password_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Actualizar contraseña de un usuario

    - Admin: puede cambiar contraseña de cualquier usuario
    - Usuario: solo puede cambiar su propia contraseña

    Body: {"new_password": "nueva_contraseña"}
    """
    new_password = password_data.get("new_password")
    if not new_password or len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe tener al menos 8 caracteres"
        )

    user = user_crud.user.get(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    # Verificar permisos
    current_user_id = int(current_user["user_id"])
    user_role = current_user.get("role")

    if user_role != "admin" and user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para cambiar la contraseña de este usuario"
        )

    user = user_crud.user.update_password(db, user_id, new_password)
    return user


@router.patch("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: int,
    role_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    Actualizar rol de un usuario

    - Solo admin
    - Roles disponibles: client, technician, admin

    Body: {"role": "admin"}
    """
    new_role_str = role_data.get("role")
    if not new_role_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El campo 'role' es requerido"
        )

    try:
        new_role = UserRole(new_role_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rol inválido. Roles disponibles: {[r.value for r in UserRole]}"
        )

    user = user_crud.user.get(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    user = user_crud.user.update_role(db, user_id, new_role)
    return user


@router.patch("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    Desactivar un usuario (soft delete)

    - Solo admin
    - No elimina el usuario, solo marca is_active=False
    """
    user = user_crud.user.get(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    # Prevenir desactivar el propio usuario
    current_user_id = int(current_user["user_id"])
    if user_id == current_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes desactivar tu propio usuario"
        )

    user = user_crud.user.deactivate(db, user_id)
    return user


@router.patch("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    Reactivar un usuario desactivado

    - Solo admin
    """
    user = user_crud.user.get(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    user = user_crud.user.activate(db, user_id)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    Eliminar un usuario permanentemente (hard delete)

    - Solo admin
    - ADVERTENCIA: Esta acción es irreversible
    - Considera usar /deactivate en su lugar
    """
    user = user_crud.user.get(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    # Prevenir eliminar el propio usuario
    current_user_id = int(current_user["user_id"])
    if user_id == current_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminar tu propio usuario"
        )

    user_crud.user.delete(db, user_id)
    return None
