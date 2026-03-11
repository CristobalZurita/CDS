from typing import Optional
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, status, Request, Query, HTTPException, Depends
from app.core.config import settings
from app.core.dependencies import get_optional_user
from app.utils.uploads import validate_image, save_upload
from app.core.ratelimit import limiter
from app.services.logging_service import create_audit
from app.services.instrument_sync_service import run_instrument_sync

# ADITIVO: Importar Cloudinary service si está disponible
try:
    from app.services.cloudinary_service import (
        is_cloudinary_enabled,
        upload_image as upload_to_cloudinary,
    )
    CLOUDINARY_AVAILABLE = True
except ImportError:
    CLOUDINARY_AVAILABLE = False

router = APIRouter(prefix="/uploads", tags=["uploads"])


async def require_upload_access(user: Optional[dict] = Depends(get_optional_user)) -> Optional[dict]:
    if user is not None:
        return user
    if settings.enable_public_uploads:
        return None
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


def _resolve_destination(destination: str) -> tuple[str, str | None]:
    target = (destination or "uploads").lower()
    if target == "uploads":
        return "uploads/images", "/uploads/images"
    if target == "instrumentos":
        return "public/images/instrumentos", "/images/instrumentos"
    if target == "inventario":
        return "public/images/INVENTARIO", "/images/INVENTARIO"
    raise HTTPException(status_code=400, detail="Destino inválido. Use uploads, instrumentos o inventario")


@router.post("/images", status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")  # limit image uploads to protect abuse
async def upload_image(
    request: Request,
    file: UploadFile = File(...),
    destination: str = Query("uploads", description="uploads|instrumentos|inventario"),
    auto_sync_instruments: bool = Query(False, description="Ejecuta sync luego de guardar"),
    user: Optional[dict] = Depends(require_upload_access),
):
    """Upload de imagen con validación. Soporta destino estándar o carpeta de instrumentos.
    
    ADITIVO: Si CLOUDINARY_URL está configurado, sube a Cloudinary.
    Si no, guarda localmente (comportamiento anterior).
    """
    await validate_image(file)

    destination = (destination or "uploads").lower()
    if destination in {"instrumentos", "inventario"} and (not user or user.get("role") != "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Solo administradores.",
        )
    is_instruments_destination = destination == "instrumentos"
    
    # ADITIVO: Verificar si usar Cloudinary o local
    use_cloudinary = CLOUDINARY_AVAILABLE and is_cloudinary_enabled()
    
    if use_cloudinary:
        # Subir a Cloudinary
        result = await upload_to_cloudinary(file, destination=destination)
        path = result["path"]
        public_path = result["public_path"]
        cloudinary_info = {
            "public_id": result.get("cloudinary_public_id"),
            "format": result.get("format"),
            "bytes": result.get("bytes"),
        }
    else:
        # Guardar localmente (comportamiento original)
        dest_dir, public_root = _resolve_destination(destination)
        
        if is_instruments_destination and not Path(file.filename or "").suffix.lower() == ".webp":
            raise HTTPException(status_code=400, detail="Para instrumentos solo se permiten archivos .webp")
        
        path = await save_upload(file, dest_dir=dest_dir)
        public_path = f"{public_root}/{Path(path).name}" if public_root else None
        cloudinary_info = None

    sync_payload = None
    # Solo hacer sync si es guardado local de instrumentos
    if not use_cloudinary and (is_instruments_destination or auto_sync_instruments):
        sync_payload = run_instrument_sync(force=False, trigger="upload")

    # Audit upload
    try:
        ip = None
        if request.client:
            ip = request.client.host
        create_audit(
            event_type="upload.image",
            user_id=(int(user["user_id"]) if user and user.get("user_id") else None),
            ip_address=ip,
            details={
                "path": path,
                "public_path": public_path,
                "filename": file.filename,
                "destination": destination,
                "storage": "cloudinary" if use_cloudinary else "local",
                "cloudinary": cloudinary_info,
                "sync": sync_payload,
            },
            message="Image uploaded",
        )
    except Exception:
        pass

    response = {
        "path": path,
        "public_path": public_path,
        "filename": file.filename,
        "destination": destination,
        "storage": "cloudinary" if use_cloudinary else "local",
        "sync": sync_payload,
    }
    
    # Incluir info de Cloudinary si aplica
    if cloudinary_info:
        response["cloudinary"] = cloudinary_info
    
    return response


@router.post("/instrumentos", status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
async def upload_instrument_image(
    request: Request,
    file: UploadFile = File(...),
    user: Optional[dict] = Depends(require_upload_access),
):
    """
    Upload directo a carpeta de instrumentos con auto-sync inmediato.
    """
    return await upload_image(
        request=request,
        file=file,
        destination="instrumentos",
        auto_sync_instruments=True,
        user=user,
    )
