from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.invoice import Invoice, InvoiceStatus
from app.models.payment import Payment
from app.models.repair import Repair
from app.models.stock import Stock
from app.models.user import User
from app.models.warranty import Warranty, WarrantyClaim, WarrantyStatus


class ReportingDashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_dashboard_stats(self) -> Dict[str, Any]:
        now = datetime.utcnow()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        total_users = self.db.query(func.count(User.id)).scalar() or 0
        total_clients = self.db.query(func.count(Client.id)).scalar() or 0
        total_repairs = self.db.query(func.count(Repair.id)).scalar() or 0
        repairs_by_status = self._get_repairs_by_status()
        repairs_this_month = (
            self.db.query(func.count(Repair.id))
            .filter(Repair.created_at >= start_of_month)
            .scalar()
            or 0
        )
        revenue_stats = self._get_revenue_stats(start_of_month)
        alerts = self._get_alerts()

        return {
            "users": total_users,
            "clients": total_clients,
            "repairs": total_repairs,
            "repairs_this_month": repairs_this_month,
            "repairs_by_status": repairs_by_status,
            "pending_repairs": repairs_by_status.get(1, 0) + repairs_by_status.get(2, 0),
            "active_repairs": repairs_by_status.get(3, 0)
            + repairs_by_status.get(4, 0)
            + repairs_by_status.get(5, 0)
            + repairs_by_status.get(6, 0),
            "completed_repairs": repairs_by_status.get(7, 0) + repairs_by_status.get(8, 0),
            "cancelled_repairs": repairs_by_status.get(9, 0),
            "revenue": revenue_stats,
            "alerts": alerts,
            "alerts_count": len(alerts),
            "generated_at": now.isoformat(),
        }

    def _get_repairs_by_status(self) -> Dict[int, int]:
        results = (
            self.db.query(Repair.status_id, func.count(Repair.id))
            .group_by(Repair.status_id)
            .all()
        )
        return {status_id: count for status_id, count in results}

    def _get_revenue_stats(self, start_of_month: datetime) -> Dict[str, Any]:
        total_invoiced = (
            self.db.query(func.sum(Invoice.total))
            .filter(Invoice.status == InvoiceStatus.PAID.value)
            .scalar()
            or 0
        )
        invoiced_this_month = (
            self.db.query(func.sum(Invoice.total))
            .filter(
                Invoice.status == InvoiceStatus.PAID.value,
                Invoice.paid_at >= start_of_month,
            )
            .scalar()
            or 0
        )
        pending_collection = (
            self.db.query(func.sum(Invoice.amount_due))
            .filter(
                Invoice.status.in_(
                    [
                        InvoiceStatus.SENT.value,
                        InvoiceStatus.VIEWED.value,
                        InvoiceStatus.PARTIAL.value,
                        InvoiceStatus.OVERDUE.value,
                    ]
                )
            )
            .scalar()
            or 0
        )
        payments_collected = (
            self.db.query(func.sum(Payment.amount))
            .filter(Payment.status == "success")
            .scalar()
            or 0
        )
        payments_this_month = (
            self.db.query(func.sum(Payment.amount))
            .filter(
                Payment.status == "success",
                Payment.created_at >= start_of_month,
            )
            .scalar()
            or 0
        )
        return {
            "total_invoiced": total_invoiced,
            "invoiced_this_month": invoiced_this_month,
            "pending_collection": pending_collection,
            "payments_collected": payments_collected,
            "payments_this_month": payments_this_month,
        }

    def _get_alerts(self) -> List[Dict[str, Any]]:
        alerts: List[Dict[str, Any]] = []

        low_stock = (
            self.db.query(Stock)
            .filter(Stock.quantity <= Stock.minimum_stock)
            .count()
        )
        if low_stock > 0:
            alerts.append(
                {
                    "type": "low_stock",
                    "severity": "warning",
                    "message": f"{low_stock} productos con stock bajo",
                    "count": low_stock,
                }
            )

        overdue_invoices = (
            self.db.query(Invoice)
            .filter(Invoice.status == InvoiceStatus.OVERDUE.value)
            .count()
        )
        if overdue_invoices > 0:
            alerts.append(
                {
                    "type": "overdue_invoices",
                    "severity": "danger",
                    "message": f"{overdue_invoices} facturas vencidas",
                    "count": overdue_invoices,
                }
            )

        expiring_warranties = (
            self.db.query(Warranty)
            .filter(
                Warranty.status == WarrantyStatus.ACTIVE.value,
                Warranty.end_date <= datetime.utcnow() + timedelta(days=7),
                Warranty.end_date > datetime.utcnow(),
            )
            .count()
        )
        if expiring_warranties > 0:
            alerts.append(
                {
                    "type": "expiring_warranties",
                    "severity": "info",
                    "message": f"{expiring_warranties} garantías por expirar",
                    "count": expiring_warranties,
                }
            )

        pending_claims = (
            self.db.query(WarrantyClaim)
            .filter(WarrantyClaim.status.in_(["submitted", "under_review"]))
            .count()
        )
        if pending_claims > 0:
            alerts.append(
                {
                    "type": "pending_claims",
                    "severity": "warning",
                    "message": f"{pending_claims} reclamos pendientes",
                    "count": pending_claims,
                }
            )

        return alerts
