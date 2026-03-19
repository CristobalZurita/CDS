"""
ReportingService - fachada estable para reportes y KPIs.
Mantiene el contrato existente y delega por subdominio interno.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.services.reporting_dashboard_service import ReportingDashboardService
from app.services.reporting_finance_service import ReportingFinanceService
from app.services.reporting_operations_service import ReportingOperationsService


class ReportingService:
    """Fachada estable para reportes del dashboard."""

    def __init__(self, db: Session):
        self.db = db
        self.dashboard = ReportingDashboardService(db)
        self.finance = ReportingFinanceService(db)
        self.operations = ReportingOperationsService(db)

    def get_dashboard_stats(self) -> Dict[str, Any]:
        return self.dashboard.get_dashboard_stats()

    def get_repairs_report(
        self,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        status_id: Optional[int] = None,
        technician_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        return self.operations.get_repairs_report(
            from_date=from_date,
            to_date=to_date,
            status_id=status_id,
            technician_id=technician_id,
        )

    def get_repairs_timeline(
        self,
        days: int = 30,
        group_by: str = "day",
    ) -> List[Dict[str, Any]]:
        return self.operations.get_repairs_timeline(days=days, group_by=group_by)

    def get_revenue_report(
        self,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        return self.finance.get_revenue_report(from_date=from_date, to_date=to_date)

    def get_revenue_timeline(self, months: int = 12) -> List[Dict[str, Any]]:
        return self.finance.get_revenue_timeline(months=months)

    def get_clients_report(self) -> Dict[str, Any]:
        return self.operations.get_clients_report()

    def get_inventory_report(self) -> Dict[str, Any]:
        return self.operations.get_inventory_report()

    def get_technician_performance(
        self,
        technician_id: Optional[int] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        return self.operations.get_technician_performance(
            technician_id=technician_id,
            from_date=from_date,
            to_date=to_date,
        )

    def get_warranty_report(self) -> Dict[str, Any]:
        return self.operations.get_warranty_report()

    def get_turnaround_stats(self) -> Dict[str, Any]:
        return self.operations.get_turnaround_stats()

    def get_overdue_repairs(self, threshold_days: int = 30) -> Dict[str, Any]:
        return self.operations.get_overdue_repairs(threshold_days=threshold_days)

    def get_lead_conversion(self) -> Dict[str, Any]:
        return self.operations.get_lead_conversion()

    def get_top_models(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self.operations.get_top_models(limit=limit)

    def get_client_return_rate(self) -> Dict[str, Any]:
        return self.operations.get_client_return_rate()

    def export_repairs_csv(
        self,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        return self.operations.export_repairs_csv(from_date=from_date, to_date=to_date)
