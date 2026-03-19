from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.invoice import Invoice, InvoiceStatus


class ReportingFinanceService:
    def __init__(self, db: Session):
        self.db = db

    def get_revenue_report(
        self,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        query = self.db.query(Invoice).filter(Invoice.status != InvoiceStatus.VOID.value)

        if from_date:
            query = query.filter(Invoice.issue_date >= from_date)
        if to_date:
            query = query.filter(Invoice.issue_date <= to_date)

        invoices = query.all()
        total_invoiced = sum(invoice.total for invoice in invoices)
        total_paid = sum(invoice.amount_paid for invoice in invoices)
        total_pending = sum(
            invoice.amount_due
            for invoice in invoices
            if invoice.status
            not in [InvoiceStatus.PAID.value, InvoiceStatus.VOID.value]
        )

        by_status = defaultdict(lambda: {"count": 0, "total": 0})
        for invoice in invoices:
            by_status[invoice.status]["count"] += 1
            by_status[invoice.status]["total"] += invoice.total

        by_month = defaultdict(lambda: {"invoiced": 0, "paid": 0})
        for invoice in invoices:
            month_key = invoice.issue_date.strftime("%Y-%m")
            by_month[month_key]["invoiced"] += invoice.total
            by_month[month_key]["paid"] += invoice.amount_paid

        return {
            "total_invoiced": total_invoiced,
            "total_paid": total_paid,
            "total_pending": total_pending,
            "collection_rate": round(total_paid / total_invoiced * 100, 2)
            if total_invoiced > 0
            else 0,
            "invoice_count": len(invoices),
            "by_status": dict(by_status),
            "by_month": dict(by_month),
        }

    def get_revenue_timeline(self, months: int = 12) -> List[Dict[str, Any]]:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=months * 30)

        invoices = (
            self.db.query(Invoice)
            .filter(
                Invoice.issue_date >= start_date,
                Invoice.status != InvoiceStatus.VOID.value,
            )
            .all()
        )

        timeline = defaultdict(lambda: {"invoiced": 0, "paid": 0, "count": 0})
        for invoice in invoices:
            month_key = invoice.issue_date.strftime("%Y-%m")
            timeline[month_key]["invoiced"] += invoice.total
            timeline[month_key]["paid"] += invoice.amount_paid
            timeline[month_key]["count"] += 1

        return [{"month": key, **value} for key, value in sorted(timeline.items())]
