from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.invoice import Invoice, InvoiceStatus
from app.models.payment import Payment
from app.services.invoice_support import get_invoice_or_404


class InvoicePaymentService:
    def __init__(self, db: Session):
        self.db = db

    def update_status(
        self,
        invoice_id: int,
        new_status: str,
        user_id: Optional[int] = None,
        reason: Optional[str] = None,
    ) -> Invoice:
        invoice = get_invoice_or_404(self.db, invoice_id)
        current = invoice.status
        valid_transitions = {
            InvoiceStatus.DRAFT.value: [InvoiceStatus.SENT.value, InvoiceStatus.VOID.value],
            InvoiceStatus.SENT.value: [
                InvoiceStatus.VIEWED.value,
                InvoiceStatus.PAID.value,
                InvoiceStatus.PARTIAL.value,
                InvoiceStatus.OVERDUE.value,
                InvoiceStatus.VOID.value,
            ],
            InvoiceStatus.VIEWED.value: [
                InvoiceStatus.PAID.value,
                InvoiceStatus.PARTIAL.value,
                InvoiceStatus.OVERDUE.value,
                InvoiceStatus.VOID.value,
            ],
            InvoiceStatus.PARTIAL.value: [InvoiceStatus.PAID.value, InvoiceStatus.VOID.value],
            InvoiceStatus.OVERDUE.value: [
                InvoiceStatus.PAID.value,
                InvoiceStatus.PARTIAL.value,
                InvoiceStatus.VOID.value,
            ],
        }

        if current not in valid_transitions or new_status not in valid_transitions.get(current, []):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Transición no válida: {current} -> {new_status}",
            )

        invoice.status = new_status
        if new_status == InvoiceStatus.SENT.value:
            invoice.sent_at = datetime.utcnow()
        elif new_status == InvoiceStatus.VIEWED.value:
            invoice.viewed_at = datetime.utcnow()
        elif new_status == InvoiceStatus.PAID.value:
            invoice.paid_at = datetime.utcnow()
            invoice.amount_due = 0
        elif new_status == InvoiceStatus.VOID.value:
            invoice.voided_at = datetime.utcnow()
            invoice.voided_by = user_id
            invoice.void_reason = reason

        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def record_payment(
        self,
        invoice_id: int,
        amount: int,
        payment_method: str = "cash",
        transaction_id: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> Payment:
        invoice = get_invoice_or_404(self.db, invoice_id)

        if invoice.status == InvoiceStatus.VOID.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede pagar una factura anulada",
            )
        if invoice.status == InvoiceStatus.PAID.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La factura ya está pagada",
            )

        from app.models.payment import PaymentStatus

        payment = Payment(
            invoice_id=invoice_id,
            repair_id=invoice.repair_id,
            user_id=user_id,
            amount=amount,
            payment_method=payment_method,
            transaction_id=transaction_id,
            status=PaymentStatus.SUCCESS,
            payment_date=datetime.utcnow(),
        )
        self.db.add(payment)

        invoice.amount_paid += amount
        invoice.amount_due = max(0, invoice.total - invoice.amount_paid)

        if invoice.amount_paid >= invoice.total:
            invoice.status = InvoiceStatus.PAID.value
            invoice.paid_at = datetime.utcnow()
        elif invoice.amount_paid > 0:
            invoice.status = InvoiceStatus.PARTIAL.value

        self.db.commit()
        self.db.refresh(payment)
        return payment

    def get_overdue_invoices(self) -> List[Invoice]:
        now = datetime.utcnow()
        return (
            self.db.query(Invoice)
            .filter(
                Invoice.status.in_(
                    [
                        InvoiceStatus.SENT.value,
                        InvoiceStatus.VIEWED.value,
                        InvoiceStatus.PARTIAL.value,
                    ]
                ),
                Invoice.due_date < now,
            )
            .all()
        )

    def mark_overdue(self) -> int:
        overdue = self.get_overdue_invoices()
        count = 0
        for invoice in overdue:
            if invoice.status != InvoiceStatus.OVERDUE.value:
                invoice.status = InvoiceStatus.OVERDUE.value
                count += 1
        self.db.commit()
        return count
