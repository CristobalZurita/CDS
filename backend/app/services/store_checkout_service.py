"""
Store Checkout Service
======================
Lógica para checkout público de tienda con verificación de email.

Flujo:
  1. create_guest_checkout()  — crea Lead + PurchaseRequest en draft,
                                genera token de 24h, envía email de verificación.
  2. verify_checkout_token()  — valida token, marca lead como verificado,
                                activa la solicitud (pending_payment).

ADITIVO: nuevo servicio, no modifica lógica existente.
"""

import logging
import secrets
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.lead import Lead
from app.models.payment import Payment, PaymentStatus
from app.models.purchase_request import PurchaseRequest, PurchaseRequestItem
from app.services.client_portal_service import (
    parse_product_meta,
    product_sellable_stock,
    product_store_enabled,
)
from app.services.email_service import EmailService, build_public_url
from app.services.purchase_request_service import (
    _apply_request_stock_state,
    _request_total,
)
from app.models.inventory import Product

logger = logging.getLogger(__name__)

_VERIFICATION_TOKEN_HOURS = 24


def _generate_token() -> str:
    return secrets.token_urlsafe(48)


def create_guest_checkout(
    db: Session,
    nombre: str,
    email: str,
    telefono: str | None,
    items_payload: list[dict],
    shipping_key: str,
    shipping_label: str,
    notes: str | None,
    ip_address: str | None,
    user_agent: str | None,
) -> dict:
    """
    Crea un Lead no verificado + PurchaseRequest en estado 'draft'.
    Genera token de verificación y envía email al comprador.
    """
    if not nombre or not nombre.strip():
        raise HTTPException(status_code=400, detail="El nombre es requerido")
    if not email or not email.strip():
        raise HTTPException(status_code=400, detail="El email es requerido")
    if not items_payload:
        raise HTTPException(status_code=400, detail="El carrito está vacío")

    # Validar y preparar items server-side (precios desde BD, nunca del browser)
    prepared_items = []
    for raw in items_payload:
        product_id = int(raw.get("product_id") or 0)
        quantity = int(raw.get("quantity") or 0)
        if product_id <= 0 or quantity <= 0:
            raise HTTPException(status_code=400, detail="Producto o cantidad inválida")

        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Producto no encontrado: {product_id}")
        if not getattr(product, "category", None):
            from app.models.category import Category
            product.category = db.query(Category).filter(Category.id == product.category_id).first()
        if not product_store_enabled(product):
            raise HTTPException(
                status_code=400,
                detail=f"Producto no disponible en tienda: {product.sku}",
            )

        sellable = product_sellable_stock(db, product)
        if sellable < quantity:
            raise HTTPException(
                status_code=409,
                detail=f"Stock insuficiente para {product.sku}: disponibles {sellable}, solicitados {quantity}",
            )

        prepared_items.append({
            "product_id": product.id,
            "sku": product.sku,
            "name": product.name,
            "quantity": quantity,
            "unit_price": float(product.price or 0),
        })

    expires_at = datetime.utcnow() + timedelta(hours=_VERIFICATION_TOKEN_HOURS)
    token = _generate_token()

    lead = Lead(
        nombre=nombre.strip(),
        email=email.strip().lower(),
        telefono=(telefono or "").strip() or None,
        source="tienda",
        status="new",
        email_verified=False,
        verification_token=token,
        verification_token_expires_at=expires_at,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(lead)
    db.flush()

    note_parts = [f"Compra tienda web — {shipping_label}"]
    if notes:
        note_parts.append(f"Nota: {notes.strip()}")

    req = PurchaseRequest(
        lead_id=lead.id,
        status="draft",
        notes=" | ".join(note_parts),
    )
    db.add(req)
    db.flush()

    for item in prepared_items:
        db.add(PurchaseRequestItem(
            request_id=req.id,
            product_id=item["product_id"],
            sku=item["sku"],
            name=item["name"],
            quantity=item["quantity"],
            unit_price=item["unit_price"],
            status="suggested",
        ))

    db.commit()

    verification_url = build_public_url(f"/tienda/verificar/{token}")
    email_sent = False
    email_warning = None
    try:
        email_sent = EmailService().send_store_order_verification_email(
            email=lead.email,
            nombre=lead.nombre,
            verification_url=verification_url,
            order_id=req.id,
        )
        if not email_sent:
            email_warning = "No se pudo enviar el email de confirmación. El taller recibirá tu solicitud y se contactará contigo."
    except Exception as exc:
        logger.warning("store_checkout: email de verificación no enviado: %s", exc)
        email_warning = "No se pudo enviar el email de confirmación. El taller recibirá tu solicitud y se contactará contigo."

    return {
        "ok": True,
        "request_id": req.id,
        "email": lead.email,
        "message": "Revisa tu email para confirmar el pedido." if email_sent else "Pedido recibido. El taller se comunicará contigo.",
        "email_sent": email_sent,
        "warning": email_warning,
    }


def verify_checkout_token(db: Session, token: str) -> dict:
    """
    Valida el token de verificación, marca el lead como verificado
    y activa la PurchaseRequest (pending_payment con Payment pendiente).
    """
    if not token:
        raise HTTPException(status_code=400, detail="Token inválido")

    lead = db.query(Lead).filter(Lead.verification_token == token).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Link inválido o ya utilizado")

    if lead.email_verified:
        # Ya verificado — buscar la solicitud y devolver estado actual
        req = (
            db.query(PurchaseRequest)
            .filter(PurchaseRequest.lead_id == lead.id)
            .order_by(PurchaseRequest.id.desc())
            .first()
        )
        return {
            "ok": True,
            "already_verified": True,
            "request_id": req.id if req else None,
            "status": req.status if req else None,
            "message": "Tu pedido ya estaba confirmado.",
        }

    if (
        lead.verification_token_expires_at
        and lead.verification_token_expires_at < datetime.utcnow()
    ):
        raise HTTPException(
            status_code=410,
            detail="El link de verificación venció. Realiza el pedido nuevamente.",
        )

    req = (
        db.query(PurchaseRequest)
        .filter(
            PurchaseRequest.lead_id == lead.id,
            PurchaseRequest.status == "draft",
        )
        .order_by(PurchaseRequest.id.desc())
        .first()
    )
    if not req:
        raise HTTPException(status_code=404, detail="No se encontró la solicitud asociada")

    # Verificar stock antes de activar
    for item in (req.items or []):
        if not item.product_id:
            continue
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            continue
        sellable = product_sellable_stock(db, product)
        if sellable < item.quantity:
            raise HTTPException(
                status_code=409,
                detail=f"Stock insuficiente para {item.sku or item.name}: disponibles {sellable}",
            )

    # Activar solicitud
    previous_status = req.status
    req.status = "pending_payment"

    total = int(round(_request_total(req)))
    due_date = datetime.utcnow() + timedelta(days=3)

    payment = Payment(
        purchase_request_id=req.id,
        amount=total,
        payment_method="transfer",
        transaction_id=f"REQ-{req.id}-{int(datetime.utcnow().timestamp())}",
        status=PaymentStatus.PENDING,
        payment_due_date=due_date,
        payment_processor="manual",
        currency="CLP",
    )
    db.add(payment)

    _apply_request_stock_state(
        db,
        req,
        previous_status=previous_status,
        next_status=req.status,
        user_id=None,
    )

    # Marcar lead como verificado y limpiar token (un solo uso)
    lead.email_verified = True
    lead.verification_token = None
    lead.verification_token_expires_at = None

    db.commit()

    return {
        "ok": True,
        "already_verified": False,
        "request_id": req.id,
        "status": req.status,
        "message": "Pedido confirmado. El taller procesará tu solicitud.",
    }
