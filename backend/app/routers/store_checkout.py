"""
Store Checkout Router
=====================
Endpoints públicos para checkout de tienda con verificación de email.

Routes:
  POST /store/checkout          — crea solicitud guest + envía email de verificación
  GET  /store/verify/{token}    — confirma email y activa la solicitud

ADITIVO: nuevo router, no modifica existentes.
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.ratelimit import limiter
from app.services.store_checkout_service import create_guest_checkout, verify_checkout_token

router = APIRouter(prefix="/store", tags=["Store Checkout"])


@router.post("/checkout")
@limiter.limit("10/minute")
def guest_checkout(payload: dict, request: Request, db: Session = Depends(get_db)):
    """
    Checkout público de tienda (sin autenticación).
    Crea Lead + PurchaseRequest en draft y envía email de verificación.
    """
    return create_guest_checkout(
        db=db,
        nombre=str(payload.get("nombre") or "").strip(),
        email=str(payload.get("email") or "").strip(),
        telefono=str(payload.get("telefono") or "").strip() or None,
        items_payload=payload.get("items") or [],
        shipping_key=str(payload.get("shipping_key") or "pickup"),
        shipping_label=str(payload.get("shipping_label") or "Retiro en taller"),
        notes=str(payload.get("notes") or "").strip() or None,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )


@router.get("/verify/{token}")
def verify_order(token: str, db: Session = Depends(get_db)):
    """
    Confirma el email del comprador y activa la PurchaseRequest.
    Sin autenticación — el token es el mecanismo de seguridad.
    """
    return verify_checkout_token(db=db, token=token)
