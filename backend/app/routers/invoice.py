"""
Router de Facturas
==================
Endpoints para gestión de facturas.
ADITIVO: Nuevo router, no modifica existentes.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_admin
from app.services.invoice_service import InvoiceService
from app.models.invoice import Invoice, InvoiceItem, InvoiceStatus, InvoiceType

router = APIRouter(prefix="/invoices", tags=["Invoices"])


# ============================================================================
# CRUD DE FACTURAS
# ============================================================================

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_invoice(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Crear nueva factura.

    Body:
    - client_id: ID del cliente (opcional)
    - repair_id: ID de reparación (opcional)
    - invoice_type: Tipo (invoice, quote, credit_note, receipt)
    - items: Lista de items [{description, quantity, unit_price, ...}]
    - due_days: Días para vencimiento (default: 30)
    - tax_rate: Tasa IVA (default: 19.0)
    - notes: Notas para cliente
    """
    svc = InvoiceService(db)

    user_id = int(user.get("user_id")) if user and user.get("user_id") else None

    invoice = svc.create_invoice(
        client_id=payload.get("client_id"),
        repair_id=payload.get("repair_id"),
        invoice_type=payload.get("invoice_type", InvoiceType.INVOICE.value),
        items=payload.get("items", []),
        due_days=payload.get("due_days", 30),
        tax_rate=payload.get("tax_rate", 19.0),
        notes=payload.get("notes"),
        created_by=user_id
    )

    return invoice


@router.post("/from-repair/{repair_id}", status_code=status.HTTP_201_CREATED)
def create_invoice_from_repair(
    repair_id: int,
    include_labor: bool = True,
    include_parts: bool = True,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Crear factura automáticamente desde una reparación"""
    svc = InvoiceService(db)
    user_id = int(user.get("user_id")) if user and user.get("user_id") else None

    return svc.create_from_repair(
        repair_id=repair_id,
        include_labor=include_labor,
        include_parts=include_parts,
        created_by=user_id
    )


@router.get("/")
def list_invoices(
    client_id: Optional[int] = None,
    repair_id: Optional[int] = None,
    status: Optional[str] = None,
    invoice_type: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Listar facturas con filtros.

    Query params:
    - client_id: Filtrar por cliente
    - repair_id: Filtrar por reparación
    - status: Filtrar por estado (draft, sent, paid, etc.)
    - invoice_type: Filtrar por tipo
    - from_date: Fecha desde (ISO format)
    - to_date: Fecha hasta (ISO format)
    """
    svc = InvoiceService(db)

    # Parsear fechas
    from_dt = datetime.fromisoformat(from_date) if from_date else None
    to_dt = datetime.fromisoformat(to_date) if to_date else None

    return svc.list_invoices(
        client_id=client_id,
        repair_id=repair_id,
        status=status,
        invoice_type=invoice_type,
        from_date=from_dt,
        to_date=to_dt,
        limit=limit,
        offset=offset
    )


@router.get("/summary")
def get_invoices_summary(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_admin)
):
    """Obtener resumen de facturación (solo admin)"""
    svc = InvoiceService(db)

    from_dt = datetime.fromisoformat(from_date) if from_date else None
    to_dt = datetime.fromisoformat(to_date) if to_date else None

    return svc.get_summary(from_date=from_dt, to_date=to_dt)


@router.get("/overdue")
def get_overdue_invoices(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Obtener facturas vencidas"""
    svc = InvoiceService(db)
    return svc.get_overdue_invoices()


@router.get("/{invoice_id}")
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Obtener detalle de factura"""
    svc = InvoiceService(db)
    return svc.get_invoice(invoice_id)


@router.get("/by-number/{invoice_number}")
def get_invoice_by_number(
    invoice_number: str,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Obtener factura por número"""
    svc = InvoiceService(db)
    invoice = svc.get_by_number(invoice_number)
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return invoice


# ============================================================================
# ITEMS DE FACTURA
# ============================================================================

@router.post("/{invoice_id}/items", status_code=status.HTTP_201_CREATED)
def add_invoice_item(
    invoice_id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Agregar item a factura.

    Body:
    - description: Descripción del item
    - quantity: Cantidad (default: 1)
    - unit_price: Precio unitario en centavos
    - item_type: Tipo (service, part, labor, discount)
    - unit: Unidad (u, hr, kg, etc.)
    """
    svc = InvoiceService(db)

    return svc.add_item(
        invoice_id=invoice_id,
        description=payload.get("description", ""),
        quantity=payload.get("quantity", 1),
        unit_price=payload.get("unit_price", 0),
        item_type=payload.get("item_type", "service"),
        unit=payload.get("unit", "u"),
        discount=payload.get("discount", 0),
        product_id=payload.get("product_id"),
        component_table=payload.get("component_table"),
        component_id=payload.get("component_id")
    )


@router.delete("/{invoice_id}/items/{item_id}")
def remove_invoice_item(
    invoice_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Eliminar item de factura"""
    svc = InvoiceService(db)
    svc.remove_item(invoice_id, item_id)
    return {"ok": True, "message": "Item eliminado"}


# ============================================================================
# ESTADOS DE FACTURA
# ============================================================================

@router.post("/{invoice_id}/send")
def send_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Marcar factura como enviada"""
    svc = InvoiceService(db)
    user_id = int(user.get("user_id")) if user and user.get("user_id") else None

    invoice = svc.update_status(invoice_id, InvoiceStatus.SENT.value, user_id=user_id)
    return {"ok": True, "invoice": invoice}


@router.post("/{invoice_id}/mark-viewed")
def mark_invoice_viewed(
    invoice_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Marcar factura como vista por cliente"""
    svc = InvoiceService(db)
    invoice = svc.update_status(invoice_id, InvoiceStatus.VIEWED.value)
    return {"ok": True, "invoice": invoice}


@router.post("/{invoice_id}/void")
def void_invoice(
    invoice_id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_admin)
):
    """Anular factura (solo admin)"""
    svc = InvoiceService(db)
    user_id = int(user.get("user_id")) if user and user.get("user_id") else None

    invoice = svc.update_status(
        invoice_id,
        InvoiceStatus.VOID.value,
        user_id=user_id,
        reason=payload.get("reason", "Sin especificar")
    )
    return {"ok": True, "invoice": invoice}


# ============================================================================
# PAGOS
# ============================================================================

@router.post("/{invoice_id}/payments", status_code=status.HTTP_201_CREATED)
def record_payment(
    invoice_id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Registrar pago para factura.

    Body:
    - amount: Monto en centavos
    - payment_method: Método (cash, card, transfer, etc.)
    - transaction_id: ID de transacción externa (opcional)
    """
    svc = InvoiceService(db)
    user_id = int(user.get("user_id")) if user and user.get("user_id") else None

    if "amount" not in payload:
        raise HTTPException(status_code=400, detail="Monto requerido")

    payment = svc.record_payment(
        invoice_id=invoice_id,
        amount=payload["amount"],
        payment_method=payload.get("payment_method", "cash"),
        transaction_id=payload.get("transaction_id"),
        user_id=user_id
    )

    return payment


# ============================================================================
# MANTENIMIENTO
# ============================================================================

@router.post("/maintenance/mark-overdue")
def mark_overdue_invoices(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_admin)
):
    """Marcar facturas vencidas (job de mantenimiento)"""
    svc = InvoiceService(db)
    count = svc.mark_overdue()
    return {"ok": True, "marked_overdue": count}
