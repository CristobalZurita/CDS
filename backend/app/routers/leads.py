"""
Router de Leads (prospectos del cotizador público).
POST /leads  — público con Turnstile, captura datos de contacto tras cotización.
GET  /leads  — solo admin, para ver y gestionar prospectos.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.ratelimit import limiter
from app.core.dependencies import require_permission
from app.models.lead import Lead
from app.schemas.lead import LeadCreate, LeadOut

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("", response_model=LeadOut, status_code=201)
@router.post("/", response_model=LeadOut, status_code=201, include_in_schema=False)
@limiter.limit("10/minute")
def create_lead(payload: LeadCreate, request: Request, db: Session = Depends(get_db)):
    """Registra un prospecto desde el cotizador público."""
    from app.services.turnstile_service import verify_turnstile
    if not payload.turnstile_token or not verify_turnstile(
        payload.turnstile_token,
        request.client.host if request.client else None,
    ):
        raise HTTPException(status_code=400, detail="Captcha inválido")

    lead = Lead(
        nombre=payload.nombre,
        email=payload.email,
        telefono=payload.telefono,
        equipment_brand=payload.equipment_brand,
        equipment_model=payload.equipment_model,
        equipment_photo_url=payload.equipment_photo_url,
        quote_result=payload.quote_result,
        source="cotizador",
        status="new",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


@router.get("", response_model=List[LeadOut])
@router.get("/", response_model=List[LeadOut], include_in_schema=False)
def list_leads(
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("leads", "read")),
):
    """Lista todos los prospectos. Solo admin."""
    return db.query(Lead).order_by(Lead.created_at.desc()).all()


@router.patch("/{lead_id}/status")
def update_lead_status(
    lead_id: int,
    status: str,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("leads", "update")),
):
    """Actualiza el estado de un lead (new → contacted → converted)."""
    valid = {"new", "contacted", "converted"}
    if status not in valid:
        raise HTTPException(status_code=400, detail=f"Estado inválido. Usar: {valid}")
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    lead.status = status
    db.commit()
    return {"ok": True, "id": lead_id, "status": status}
