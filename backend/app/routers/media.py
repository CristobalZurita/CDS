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
import re
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


def _strip_version(url: str) -> str:
    """Quita /vNNNNNNNNNN/ de URLs de Cloudinary.
    Sin versión, Cloudinary siempre sirve el asset más reciente para ese public_id.
    """
    if not url:
        return url
    return re.sub(r'/v\d+/', '/', url)

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
    if 'secure_url' in update_payload:
        update_payload['secure_url'] = _strip_version(update_payload['secure_url'])
    create_payload = data.model_dump(exclude_none=True)
    if 'secure_url' in create_payload:
        create_payload['secure_url'] = _strip_version(create_payload['secure_url'])

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


@router.post("/assets/import-from-cloudinary")
def import_from_cloudinary(db: Session = Depends(get_db)):
    """
    Importa masivamente todos los assets de Cloudinary a media_assets.
    Hace upsert por public_id: actualiza si ya existe, inserta si es nuevo.
    Retorna conteo de insertados y actualizados.
    """
    from app.services.cloudinary_service import fetch_all_images

    resources = fetch_all_images()
    if not resources:
        return {"inserted": 0, "updated": 0, "total": 0, "message": "Cloudinary no disponible o sin imágenes."}

    inserted = 0
    updated = 0

    for r in resources:
        public_id = r.get("public_id")
        secure_url = _strip_version(r.get("url") or r.get("secure_url") or "")
        if not public_id or not secure_url:
            continue

        folder = public_id.rsplit("/", 1)[0] if "/" in public_id else ""
        original_filename = public_id.split("/")[-1]

        existing = db.query(MediaAsset).filter(MediaAsset.public_id == public_id).first()
        if existing:
            existing.secure_url = secure_url
            existing.folder = folder or existing.folder
            existing.format = r.get("format") or existing.format
            existing.bytes = r.get("bytes") or existing.bytes
            existing.width = r.get("width") or existing.width
            existing.height = r.get("height") or existing.height
            updated += 1
        else:
            asset = MediaAsset(
                public_id=public_id,
                secure_url=secure_url,
                folder=folder,
                original_filename=original_filename,
                format=r.get("format"),
                bytes=r.get("bytes"),
                width=r.get("width"),
                height=r.get("height"),
            )
            db.add(asset)
            inserted += 1

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error al importar desde Cloudinary: {e}")
        raise HTTPException(status_code=500, detail="Error al guardar los assets importados.")

    return {"inserted": inserted, "updated": updated, "total": inserted + updated}


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
