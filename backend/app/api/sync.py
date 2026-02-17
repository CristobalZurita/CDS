"""
API de sincronización de instrumentos (FastAPI).
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.services.instrument_sync_service import (
    get_current_instruments_data,
    get_instrument_sync_status,
    run_instrument_sync,
)

router = APIRouter(prefix="/instruments-sync", tags=["instruments-sync"])


@router.get("/sync")
async def get_synced_instruments():
    """
    Retorna el estado actual del JSON sincronizado sin ejecutar sync.
    """
    status = get_instrument_sync_status()
    if not status.get("json_exists"):
        raise HTTPException(status_code=404, detail="Instruments JSON not found")
    data = get_current_instruments_data()
    return {
        "success": True,
        "cached": True,
        "status": status,
        "data": data,
    }


@router.post("/sync")
async def sync_instruments(force: bool = Query(False, description="Fuerza resincronización")):
    """
    Ejecuta sincronización inmediatamente.
    """
    result = run_instrument_sync(force=force, trigger="api")
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error") or result.get("stderr") or "Sync failed")
    return {
        "success": True,
        "message": "Sincronización completada",
        "result": result,
    }


@router.get("/status")
async def sync_status():
    """
    Estado de sincronización (sin ejecutar script).
    """
    return {
        "success": True,
        "status": get_instrument_sync_status(),
    }
