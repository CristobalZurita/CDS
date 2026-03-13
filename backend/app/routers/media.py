"""
Router para gestión dinámica de medios (assets + bindings).
ADITIVO: no modifica routers existentes.

Endpoints:
  GET  /media/assets           — listar todos los assets registrados en BD
  POST /media/assets           — registrar un asset después de upload a Cloudinary
  DELETE /media/assets/{id}    — eliminar asset de BD (y opcionalmente de Cloudinary)

  GET  /media/bindings         — listar todos los bindings (slot → asset)
  PUT  /media/bindings/{slot}  — asignar/actualizar asset en un slot
  DELETE /media/bindings/{slot} — quitar binding de un slot
"""

import logging
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import SessionLocal
from app.models.media import MediaAsset, MediaBinding
from app.schemas.media import (
    MediaAssetCreate, MediaAssetOut,
    MediaBindingUpsert, MediaBindingOut,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/media", tags=["media"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─── ASSETS ──────────────────────────────────────────────────────────────────

@router.get("/assets", response_model=List[MediaAssetOut])
def list_assets(db: Session = Depends(get_db)):
    """Devuelve todos los assets registrados en la BD."""
    return db.query(MediaAsset).order_by(MediaAsset.uploaded_at.desc()).all()


@router.post("/assets", response_model=MediaAssetOut, status_code=status.HTTP_201_CREATED)
def register_asset(data: MediaAssetCreate, db: Session = Depends(get_db)):
    """
    Registra un asset en la BD después de que el frontend lo subió a Cloudinary.
    Si el public_id ya existe, actualiza sus datos (overwrite en Cloudinary).
    """
    update_payload = data.model_dump(exclude_unset=True, exclude_none=True)
    create_payload = data.model_dump(exclude_none=True)

    existing = db.query(MediaAsset).filter(MediaAsset.public_id == data.public_id).first()
    if existing:
        for field, value in update_payload.items():
            setattr(existing, field, value)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            existing = db.query(MediaAsset).filter(MediaAsset.public_id == data.public_id).first()
            if not existing:
                raise HTTPException(
                    status_code=409,
                    detail="Conflicto al actualizar el asset. Reintenta.",
                )
            for field, value in update_payload.items():
                setattr(existing, field, value)
            db.commit()
        db.refresh(existing)
        return existing

    asset = MediaAsset(**create_payload)
    db.add(asset)
    try:
        db.commit()
        db.refresh(asset)
        return asset
    except IntegrityError:
        db.rollback()
        existing = db.query(MediaAsset).filter(MediaAsset.public_id == data.public_id).first()
        if not existing:
            raise HTTPException(
                status_code=409,
                detail="Conflicto al registrar el asset. Reintenta.",
            )
        for field, value in update_payload.items():
            setattr(existing, field, value)
        db.commit()
        db.refresh(existing)
        return existing


@router.delete("/assets/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(asset_id: int, from_cloudinary: bool = False, db: Session = Depends(get_db)):
    """
    Elimina un asset de la BD.
    Si from_cloudinary=true también lo borra de Cloudinary.
    """
    asset = db.query(MediaAsset).filter(MediaAsset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset no encontrado")

    # Verificar que no tenga bindings activos
    bindings = db.query(MediaBinding).filter(MediaBinding.asset_id == asset_id).count()
    if bindings > 0:
        raise HTTPException(
            status_code=409,
            detail=f"El asset está en uso en {bindings} slot(s). Reasigna los slots antes de eliminar."
        )

    if from_cloudinary:
        try:
            from app.services.cloudinary_service import delete_image
            delete_image(asset.public_id)
        except Exception as e:
            logger.warning(f"No se pudo eliminar de Cloudinary: {e}")

    db.delete(asset)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="El asset está en uso por un slot activo. Reasigna el slot antes de eliminar.",
        )


# ─── BINDINGS ────────────────────────────────────────────────────────────────

@router.get("/bindings", response_model=List[MediaBindingOut])
def list_bindings(db: Session = Depends(get_db)):
    """
    Devuelve todos los bindings activos (slot_key → asset).
    Este endpoint lo consume el front para renderizar imágenes dinámicas.
    """
    return db.query(MediaBinding).order_by(MediaBinding.slot_key).all()


@router.put("/bindings/{slot_key:path}", response_model=MediaBindingOut)
def upsert_binding(slot_key: str, data: MediaBindingUpsert, db: Session = Depends(get_db)):
    """
    Asigna un asset a un slot (crea o actualiza).
    Ej: PUT /media/bindings/home.hero.bg   body: {"asset_id": 5}
    """
    asset = db.query(MediaAsset).filter(MediaAsset.id == data.asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset no encontrado")

    binding = db.query(MediaBinding).filter(MediaBinding.slot_key == slot_key).first()
    if binding:
        binding.asset_id = data.asset_id
        binding.label = data.label
        # Fuerza actualización temporal aunque el asset no cambie.
        binding.updated_at = datetime.utcnow()
    else:
        binding = MediaBinding(
            slot_key=slot_key,
            asset_id=data.asset_id,
            label=data.label,
        )
        db.add(binding)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="No se pudo guardar el slot por un conflicto de concurrencia.",
        )
    db.refresh(binding)
    return binding


@router.delete("/bindings/{slot_key:path}", status_code=status.HTTP_204_NO_CONTENT)
def delete_binding(slot_key: str, db: Session = Depends(get_db)):
    """Quita el binding de un slot (el asset no se elimina)."""
    binding = db.query(MediaBinding).filter(MediaBinding.slot_key == slot_key).first()
    if not binding:
        raise HTTPException(status_code=404, detail="Binding no encontrado")
    db.delete(binding)
    db.commit()
