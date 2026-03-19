from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.device import Device
from app.models.repair import Repair
from app.models.repair_component_usage import RepairComponentUsage
from app.models.stock import Stock
from app.models.user import User
from app.models.warranty import Warranty, WarrantyClaim, WarrantyStatus


class ReportingOperationsService:
    def __init__(self, db: Session):
        self.db = db

    def get_repairs_report(
        self,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        status_id: Optional[int] = None,
        technician_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        query = self.db.query(Repair)

        if from_date:
            query = query.filter(Repair.created_at >= from_date)
        if to_date:
            query = query.filter(Repair.created_at <= to_date)
        if status_id:
            query = query.filter(Repair.status_id == status_id)
        if technician_id:
            query = query.filter(Repair.assigned_to == technician_id)

        repairs = query.all()
        total_labor = sum(repair.labor_cost or 0 for repair in repairs)
        total_parts = sum(repair.parts_cost or 0 for repair in repairs)
        total_quoted = sum(repair.quoted_price or 0 for repair in repairs)
        total_cost = total_labor + total_parts

        by_status = defaultdict(int)
        for repair in repairs:
            by_status[repair.status_id] += 1

        by_technician = defaultdict(int)
        for repair in repairs:
            if repair.assigned_to:
                by_technician[repair.assigned_to] += 1

        by_priority = defaultdict(int)
        for repair in repairs:
            by_priority[repair.priority or 2] += 1

        return {
            "total_repairs": len(repairs),
            "total_labor_cost": total_labor,
            "total_parts_cost": total_parts,
            "total_cost": total_cost,
            "total_quoted": total_quoted,
            "margin": total_quoted - total_cost,
            "margin_percent": round((total_quoted - total_cost) / total_quoted * 100, 2)
            if total_quoted > 0
            else 0,
            "by_status": dict(by_status),
            "by_technician": dict(by_technician),
            "by_priority": dict(by_priority),
            "avg_labor_cost": round(total_labor / len(repairs), 2) if repairs else 0,
            "avg_parts_cost": round(total_parts / len(repairs), 2) if repairs else 0,
        }

    def get_repairs_timeline(
        self,
        days: int = 30,
        group_by: str = "day",
    ) -> List[Dict[str, Any]]:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        repairs = (
            self.db.query(Repair)
            .filter(Repair.created_at >= start_date, Repair.created_at <= end_date)
            .all()
        )

        timeline = defaultdict(lambda: {"created": 0, "completed": 0, "cancelled": 0})
        for repair in repairs:
            if group_by == "day":
                key = repair.created_at.strftime("%Y-%m-%d")
            elif group_by == "week":
                key = repair.created_at.strftime("%Y-W%W")
            else:
                key = repair.created_at.strftime("%Y-%m")

            timeline[key]["created"] += 1
            if repair.status_id in [7, 8]:
                timeline[key]["completed"] += 1
            elif repair.status_id == 9:
                timeline[key]["cancelled"] += 1

        return [{"period": key, **value} for key, value in sorted(timeline.items())]

    def get_clients_report(self) -> Dict[str, Any]:
        total_clients = self.db.query(func.count(Client.id)).scalar() or 0
        start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        new_this_month = (
            self.db.query(func.count(Client.id))
            .filter(Client.created_at >= start_of_month)
            .scalar()
            or 0
        )
        by_segment = (
            self.db.query(Client.customer_segment, func.count(Client.id))
            .group_by(Client.customer_segment)
            .all()
        )
        top_clients = (
            self.db.query(
                Client.id,
                Client.name,
                Client.total_spent,
                Client.total_repairs,
            )
            .order_by(Client.total_spent.desc())
            .limit(10)
            .all()
        )

        return {
            "total_clients": total_clients,
            "new_this_month": new_this_month,
            "by_segment": {segment or "regular": count for segment, count in by_segment},
            "top_clients": [
                {
                    "id": client.id,
                    "name": client.name,
                    "total_spent": client.total_spent or 0,
                    "total_repairs": client.total_repairs or 0,
                }
                for client in top_clients
            ],
        }

    def get_inventory_report(self) -> Dict[str, Any]:
        stocks = self.db.query(Stock).all()
        total_items = len(stocks)
        low_stock_items = sum(1 for stock in stocks if stock.quantity <= stock.minimum_stock)
        out_of_stock = sum(1 for stock in stocks if stock.quantity == 0)
        total_value = sum((stock.unit_cost or 0) * stock.quantity for stock in stocks)
        most_used = (
            self.db.query(
                RepairComponentUsage.component_id,
                RepairComponentUsage.component_table,
                func.sum(RepairComponentUsage.quantity).label("total_used"),
            )
            .group_by(
                RepairComponentUsage.component_id,
                RepairComponentUsage.component_table,
            )
            .order_by(func.sum(RepairComponentUsage.quantity).desc())
            .limit(10)
            .all()
        )

        return {
            "total_items": total_items,
            "low_stock_items": low_stock_items,
            "out_of_stock": out_of_stock,
            "total_inventory_value": total_value,
            "most_used_components": [
                {
                    "component_id": item.component_id,
                    "table": item.component_table,
                    "total_used": item.total_used,
                }
                for item in most_used
            ],
        }

    def get_technician_performance(
        self,
        technician_id: Optional[int] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        query = (
            self.db.query(
                User.id,
                User.first_name,
                User.last_name,
                func.count(Repair.id).label("total_repairs"),
                func.sum(case((Repair.status_id.in_([7, 8]), 1), else_=0)).label("completed"),
                func.sum(case((Repair.status_id == 9, 1), else_=0)).label("cancelled"),
                func.avg(Repair.labor_cost).label("avg_labor"),
            )
            .join(Repair, User.id == Repair.assigned_to, isouter=True)
        )

        if technician_id:
            query = query.filter(User.id == technician_id)
        if from_date:
            query = query.filter(Repair.created_at >= from_date)
        if to_date:
            query = query.filter(Repair.created_at <= to_date)

        results = (
            query.filter(User.role_id == 2)
            .group_by(User.id, User.first_name, User.last_name)
            .all()
        )

        return [
            {
                "technician_id": row.id,
                "name": f"{row.first_name or ''} {row.last_name or ''}".strip() or f"User {row.id}",
                "total_repairs": row.total_repairs or 0,
                "completed": row.completed or 0,
                "cancelled": row.cancelled or 0,
                "completion_rate": round((row.completed or 0) / (row.total_repairs or 1) * 100, 2),
                "avg_labor": round(row.avg_labor or 0, 2),
            }
            for row in results
        ]

    def get_warranty_report(self) -> Dict[str, Any]:
        total_warranties = self.db.query(func.count(Warranty.id)).scalar() or 0
        active_warranties = (
            self.db.query(func.count(Warranty.id))
            .filter(Warranty.status == WarrantyStatus.ACTIVE.value)
            .scalar()
            or 0
        )
        total_claims = self.db.query(func.count(WarrantyClaim.id)).scalar() or 0
        approved_claims = (
            self.db.query(func.count(WarrantyClaim.id))
            .filter(WarrantyClaim.status.in_(["approved", "in_progress", "completed"]))
            .scalar()
            or 0
        )
        rejected_claims = (
            self.db.query(func.count(WarrantyClaim.id))
            .filter(WarrantyClaim.status == "rejected")
            .scalar()
            or 0
        )
        warranty_cost = (
            self.db.query(func.sum(WarrantyClaim.actual_cost))
            .filter(WarrantyClaim.status == "completed")
            .scalar()
            or 0
        )

        return {
            "total_warranties": total_warranties,
            "active_warranties": active_warranties,
            "total_claims": total_claims,
            "approved_claims": approved_claims,
            "rejected_claims": rejected_claims,
            "approval_rate": round(approved_claims / total_claims * 100, 2)
            if total_claims > 0
            else 0,
            "total_warranty_cost": warranty_cost,
        }

    def get_turnaround_stats(self) -> Dict[str, Any]:
        completed = (
            self.db.query(Repair)
            .filter(
                Repair.completion_date.isnot(None),
                Repair.intake_date.isnot(None),
                Repair.status_id.in_([7, 8]),
            )
            .all()
        )
        if not completed:
            return {"avg_days": None, "min_days": None, "max_days": None, "count": 0}

        days_list = [
            (repair.completion_date - repair.intake_date).days
            for repair in completed
            if repair.completion_date >= repair.intake_date
        ]
        if not days_list:
            return {"avg_days": None, "min_days": None, "max_days": None, "count": 0}

        return {
            "avg_days": round(sum(days_list) / len(days_list), 1),
            "min_days": min(days_list),
            "max_days": max(days_list),
            "count": len(days_list),
        }

    def get_overdue_repairs(self, threshold_days: int = 30) -> Dict[str, Any]:
        active_status_ids = [1, 2, 3, 4, 5, 6]
        cutoff = datetime.utcnow() - timedelta(days=threshold_days)
        total_active = (
            self.db.query(func.count(Repair.id))
            .filter(Repair.status_id.in_(active_status_ids))
            .scalar()
            or 0
        )
        overdue = (
            self.db.query(func.count(Repair.id))
            .filter(
                Repair.status_id.in_(active_status_ids),
                Repair.intake_date <= cutoff,
            )
            .scalar()
            or 0
        )

        return {
            "overdue_count": overdue,
            "threshold_days": threshold_days,
            "total_active": total_active,
            "overdue_pct": round(overdue / total_active * 100, 1) if total_active > 0 else 0,
        }

    def get_lead_conversion(self) -> Dict[str, Any]:
        from app.models.lead import Lead

        total = self.db.query(func.count(Lead.id)).scalar() or 0
        converted = (
            self.db.query(func.count(Lead.id))
            .filter(Lead.status == "converted")
            .scalar()
            or 0
        )
        contacted = (
            self.db.query(func.count(Lead.id))
            .filter(Lead.status == "contacted")
            .scalar()
            or 0
        )

        return {
            "total_leads": total,
            "new": total - converted - contacted,
            "contacted": contacted,
            "converted": converted,
            "conversion_rate": round(converted / total * 100, 1) if total > 0 else 0,
        }

    def get_top_models(self, limit: int = 10) -> List[Dict[str, Any]]:
        results = (
            self.db.query(
                Device.model,
                func.count(Repair.id).label("repair_count"),
            )
            .join(Repair, Repair.device_id == Device.id)
            .group_by(Device.model)
            .order_by(func.count(Repair.id).desc())
            .limit(limit)
            .all()
        )
        return [{"model": row.model, "repair_count": row.repair_count} for row in results]

    def get_client_return_rate(self) -> Dict[str, Any]:
        subquery = (
            self.db.query(
                Device.client_id,
                func.count(Repair.id).label("repair_count"),
            )
            .join(Repair, Repair.device_id == Device.id)
            .group_by(Device.client_id)
            .subquery()
        )

        total_with_repairs = self.db.query(func.count(subquery.c.client_id)).scalar() or 0
        returning = (
            self.db.query(func.count(subquery.c.client_id))
            .filter(subquery.c.repair_count > 1)
            .scalar()
            or 0
        )

        return {
            "returning_clients": returning,
            "first_time_clients": total_with_repairs - returning,
            "total_clients_with_repairs": total_with_repairs,
            "return_rate": round(returning / total_with_repairs * 100, 1)
            if total_with_repairs > 0
            else 0,
        }

    def export_repairs_csv(
        self,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        query = self.db.query(Repair)

        if from_date:
            query = query.filter(Repair.created_at >= from_date)
        if to_date:
            query = query.filter(Repair.created_at <= to_date)

        repairs = query.all()
        return [
            {
                "id": repair.id,
                "repair_number": repair.repair_number,
                "status_id": repair.status_id,
                "priority": repair.priority,
                "problem_reported": repair.problem_reported,
                "diagnosis": repair.diagnosis,
                "work_performed": repair.work_performed,
                "labor_cost": repair.labor_cost,
                "parts_cost": repair.parts_cost,
                "quoted_price": repair.quoted_price,
                "assigned_to": repair.assigned_to,
                "created_at": repair.created_at.isoformat() if repair.created_at else None,
                "updated_at": repair.updated_at.isoformat() if repair.updated_at else None,
            }
            for repair in repairs
        ]
