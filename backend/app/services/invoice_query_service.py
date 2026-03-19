from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.invoice import Invoice, InvoiceStatus
from app.services.invoice_support import get_invoice_or_404


class InvoiceQueryService:
    def __init__(self, db: Session):
        self.db = db

    def get_invoice(self, invoice_id: int) -> Invoice:
        return get_invoice_or_404(self.db, invoice_id)

    def get_by_number(self, invoice_number: str) -> Optional[Invoice]:
        return self.db.query(Invoice).filter(Invoice.invoice_number == invoice_number).first()

    def list_invoices(
        self,
        client_id: Optional[int] = None,
        repair_id: Optional[int] = None,
        status: Optional[str] = None,
        invoice_type: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Invoice]:
        query = self.db.query(Invoice)

        if client_id:
            query = query.filter(Invoice.client_id == client_id)
        if repair_id:
            query = query.filter(Invoice.repair_id == repair_id)
        if status:
            query = query.filter(Invoice.status == status)
        if invoice_type:
            query = query.filter(Invoice.invoice_type == invoice_type)
        if from_date:
            query = query.filter(Invoice.issue_date >= from_date)
        if to_date:
            query = query.filter(Invoice.issue_date <= to_date)

        return query.order_by(Invoice.issue_date.desc()).offset(offset).limit(limit).all()

    def get_summary(
        self,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        query = self.db.query(Invoice)
        if from_date:
            query = query.filter(Invoice.issue_date >= from_date)
        if to_date:
            query = query.filter(Invoice.issue_date <= to_date)

        invoices = query.all()
        total_invoiced = sum(
            invoice.total for invoice in invoices if invoice.status != InvoiceStatus.VOID.value
        )
        total_paid = sum(invoice.amount_paid for invoice in invoices)
        total_pending = sum(
            invoice.amount_due
            for invoice in invoices
            if invoice.status not in [InvoiceStatus.VOID.value, InvoiceStatus.PAID.value]
        )

        by_status: Dict[str, int] = {}
        for invoice in invoices:
            by_status[invoice.status] = by_status.get(invoice.status, 0) + 1

        return {
            "total_invoiced": total_invoiced,
            "total_paid": total_paid,
            "total_pending": total_pending,
            "count": len(invoices),
            "by_status": by_status,
        }
