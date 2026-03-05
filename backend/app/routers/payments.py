from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List
from pydantic import ValidationError
from app.core.database import get_db
from app.core.dependencies import require_permission
from sqlalchemy.orm import Session
from app.models.payment import Payment, PaymentStatus
from app.models.audit import AuditLog
from sqlalchemy.exc import IntegrityError
from app.schemas import PaymentCreate, PaymentRead

router = APIRouter(prefix="/payments", tags=["payments"])


def _as_payment_read(payment: Payment) -> PaymentRead:
    return PaymentRead.model_validate(payment)


def _create_audit_inline(
    db: Session,
    *,
    event_type: str,
    user_id: int | None = None,
    details: Dict | None = None,
    message: str | None = None,
) -> None:
    """
    Escribe auditoría usando la MISMA sesión del endpoint para evitar locks
    cruzados en SQLite cuando hay transacciones abiertas.
    """
    try:
        db.add(
            AuditLog(
                event_type=event_type,
                user_id=user_id,
                details=details,
                message=message,
            )
        )
        db.commit()
    except Exception:
        db.rollback()


@router.post("/", response_model=PaymentRead)
async def create_payment(payload: PaymentCreate, db: Session = Depends(get_db), user: dict = Depends(require_permission("payments", "create"))):
    # Pydantic validation already ensures basic correctness
    data = payload.model_dump()

    # Idempotency: if transaction_id provided and a payment already exists, return it
    tx = data.get("transaction_id")
    if tx:
        # Be tolerant: there may be duplicates in older data or race conditions that created
        # more than one row. Use first() ordered by id so we consistently return the
        # earliest existing payment rather than raising MultipleResultsFound.
        # Prefer the most recent payment for this transaction id (highest id)
        existing = db.query(Payment).filter(Payment.transaction_id == tx).order_by(Payment.id.desc()).first()
        if existing:
            return _as_payment_read(existing)

    payment = Payment(
        user_id=data.get("user_id"),
        repair_id=data.get("repair_id"),
        purchase_request_id=data.get("purchase_request_id"),
        amount=data.get("amount"),
        payment_method=data.get("payment_method"),
        transaction_id=data.get("transaction_id"),
        status=PaymentStatus.SUCCESS if (data.get("status") or "").lower() == "success" else PaymentStatus.PENDING,
        notes=data.get("notes"),
    )
    db.add(payment)
    try:
        db.commit()
        db.refresh(payment)
    except IntegrityError:
        # Handle race: another request created the same transaction_id concurrently
        # Roll back and return the existing payment.
        db.rollback()
        existing = None
        if tx:
            existing = db.query(Payment).filter(Payment.transaction_id == tx).order_by(Payment.id.desc()).first()
        if existing:
            return _as_payment_read(existing)
        # If we couldn't find the existing row, re-raise so callers/tests notice
        raise

    # audit with richer details
    _create_audit_inline(
        db,
        event_type="payment.create",
        user_id=payment.user_id,
        details={
            "payment_id": payment.id,
            "repair_id": payment.repair_id,
            "amount": payment.amount,
            "method": payment.payment_method,
            "transaction_id": payment.transaction_id,
            "status": payment.status,
        },
        message="Payment created",
    )

    return _as_payment_read(payment)


@router.get("/", response_model=List[PaymentRead])
async def list_payments(repair_id: int = None, user_id: int = None, db: Session = Depends(get_db), user: dict = Depends(require_permission("payments", "read"))):
    q = db.query(Payment)
    if repair_id:
        q = q.filter(Payment.repair_id == repair_id)
    if user_id:
        q = q.filter(Payment.user_id == user_id)
    results = q.all()
    _create_audit_inline(
        db,
        event_type="payment.list",
        details={"repair_id": repair_id, "user_id": user_id},
        message="Payments listed",
    )
    return [_as_payment_read(payment) for payment in results]


@router.get("/{payment_id}", response_model=PaymentRead)
async def get_payment(payment_id: int, db: Session = Depends(get_db), user: dict = Depends(require_permission("payments", "read"))):
    payment = db.query(Payment).filter(Payment.id == payment_id).one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    _create_audit_inline(
        db,
        event_type="payment.get",
        details={"payment_id": payment_id},
        message="Payment fetched",
    )
    return _as_payment_read(payment)
