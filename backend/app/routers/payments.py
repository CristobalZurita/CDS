from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List
from pydantic import ValidationError
from backend.app.core.database import get_db
from sqlalchemy.orm import Session
from backend.app.models.payment import Payment, PaymentStatus
from backend.app.services.logging_service import create_audit
from sqlalchemy.exc import IntegrityError
from backend.app.schemas import PaymentCreate, PaymentRead

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/", response_model=PaymentRead)
def create_payment(payload: PaymentCreate, db: Session = Depends(get_db)):
    # Pydantic validation already ensures basic correctness
    data = payload.dict()

    # Idempotency: if transaction_id provided and a payment already exists, return it
    tx = data.get("transaction_id")
    if tx:
        # Be tolerant: there may be duplicates in older data or race conditions that created
        # more than one row. Use first() ordered by id so we consistently return the
        # earliest existing payment rather than raising MultipleResultsFound.
        # Prefer the most recent payment for this transaction id (highest id)
        existing = db.query(Payment).filter(Payment.transaction_id == tx).order_by(Payment.id.desc()).first()
        if existing:
            try:
                create_audit(event_type="payment.duplicate", user_id=existing.user_id, details={"payment_id": existing.id, "transaction_id": tx}, message="Duplicate payment request detected")
            except Exception:
                pass
            return existing

    payment = Payment(
        user_id=data.get("user_id"),
        repair_id=data.get("repair_id"),
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
            try:
                create_audit(event_type="payment.duplicate", user_id=existing.user_id, details={"payment_id": existing.id, "transaction_id": tx}, message="Duplicate payment request detected (race)")
            except Exception:
                pass
            return existing
        # If we couldn't find the existing row, re-raise so callers/tests notice
        raise

    # audit with richer details
    try:
        create_audit(event_type="payment.create", user_id=payment.user_id, details={"payment_id": payment.id, "repair_id": payment.repair_id, "amount": payment.amount, "method": payment.payment_method, "transaction_id": payment.transaction_id, "status": payment.status}, message="Payment created")
    except Exception:
        pass

    return payment


@router.get("/", response_model=List[PaymentRead])
def list_payments(repair_id: int = None, user_id: int = None, db: Session = Depends(get_db)):
    q = db.query(Payment)
    if repair_id:
        q = q.filter(Payment.repair_id == repair_id)
    if user_id:
        q = q.filter(Payment.user_id == user_id)
    results = q.all()
    try:
        create_audit(event_type="payment.list", details={"repair_id": repair_id, "user_id": user_id}, message="Payments listed")
    except Exception:
        pass
    return results


@router.get("/{payment_id}", response_model=PaymentRead)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    try:
        create_audit(event_type="payment.get", details={"payment_id": payment_id}, message="Payment fetched")
    except Exception:
        pass
    return payment
