from pathlib import Path

from fastapi import APIRouter, UploadFile, File, status, Request, Query, HTTPException
from app.utils.uploads import validate_image, save_upload
from app.core.ratelimit import limiter
from app.services.logging_service import create_audit
from app.services.instrument_sync_service import run_instrument_sync

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("/images", status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")  # limit image uploads to protect abuse
async def upload_image(
    request: Request,
    file: UploadFile = File(...),
    destination: str = Query("uploads", description="uploads|instrumentos"),
    auto_sync_instruments: bool = Query(False, description="Ejecuta sync luego de guardar"),
):
    """Upload de imagen con validación. Soporta destino estándar o carpeta de instrumentos."""
    await validate_image(file)

    destination = (destination or "uploads").lower()
    is_instruments_destination = destination == "instrumentos"
    if destination not in {"uploads", "instrumentos"}:
        raise HTTPException(status_code=400, detail="Destino inválido. Use uploads o instrumentos")

    if is_instruments_destination and not Path(file.filename or "").suffix.lower() == ".webp":
        raise HTTPException(status_code=400, detail="Para instrumentos solo se permiten archivos .webp")

    dest_dir = "public/images/instrumentos" if is_instruments_destination else "uploads/images"
    path = await save_upload(file, dest_dir=dest_dir)

    sync_payload = None
    if is_instruments_destination or auto_sync_instruments:
        sync_payload = run_instrument_sync(force=False, trigger="upload")

    # Audit upload
    try:
        ip = None
        if request.client:
            ip = request.client.host
        create_audit(
            event_type="upload.image",
            user_id=None,
            ip_address=ip,
            details={
                "path": path,
                "filename": file.filename,
                "destination": destination,
                "sync": sync_payload,
            },
            message="Image uploaded",
        )
    except Exception:
        pass

    return {
        "path": path,
        "filename": file.filename,
        "destination": destination,
        "sync": sync_payload,
    }


@router.post("/instrumentos", status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
async def upload_instrument_image(request: Request, file: UploadFile = File(...)):
    """
    Upload directo a carpeta de instrumentos con auto-sync inmediato.
    """
    return await upload_image(
        request=request,
        file=file,
        destination="instrumentos",
        auto_sync_instruments=True,
    )
