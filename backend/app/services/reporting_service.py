"""
ReportingService - Servicio de Reportes y KPIs
==============================================
Genera estadísticas, KPIs y reportes para el dashboard.
ADITIVO: Nuevo servicio, no modifica existentes.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, extract, case
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict

from app.models.repair import Repair, RepairStatus
from app.models.client import Client
from app.models.user import User
from app.models.payment import Payment
from app.models.appointment import Appointment
from app.models.stock import Stock
from app.models.stock_movement import StockMovement
from app.models.invoice import Invoice, InvoiceStatus
from app.models.warranty import Warranty, WarrantyClaim, WarrantyStatus
from app.models.repair_component_usage import RepairComponentUsage
from app.models.device import Device


class ReportingService:
    """Servicio de reportes y KPIs para dashboard"""

    def __init__(self, db: Session):
        self.db = db

    # =========================================================================
    # DASHBOARD PRINCIPAL - KPIs Rápidos
    # =========================================================================

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """
        Estadísticas principales para el dashboard.
        Retorna contadores y métricas clave.
        """
        now = datetime.utcnow()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_of_week = now - timedelta(days=now.weekday())

        # Contadores básicos
        total_users = self.db.query(func.count(User.id)).scalar() or 0
        total_clients = self.db.query(func.count(Client.id)).scalar() or 0
        total_repairs = self.db.query(func.count(Repair.id)).scalar() or 0

        # Reparaciones por estado
        repairs_by_status = self._get_repairs_by_status()

        # Reparaciones este mes
        repairs_this_month = self.db.query(func.count(Repair.id)).filter(
            Repair.created_at >= start_of_month
        ).scalar() or 0

        # Ingresos
        revenue_stats = self._get_revenue_stats(start_of_month)

        # Alertas
        alerts = self._get_alerts()

        return {
            # Contadores básicos (compatibilidad con frontend actual)
            "users": total_users,
            "clients": total_clients,
            "repairs": total_repairs,

            # KPIs extendidos
            "repairs_this_month": repairs_this_month,
            "repairs_by_status": repairs_by_status,

            # Estados específicos
            "pending_repairs": repairs_by_status.get(1, 0) + repairs_by_status.get(2, 0),
            "active_repairs": repairs_by_status.get(3, 0) + repairs_by_status.get(4, 0) +
                             repairs_by_status.get(5, 0) + repairs_by_status.get(6, 0),
            "completed_repairs": repairs_by_status.get(7, 0) + repairs_by_status.get(8, 0),
            "cancelled_repairs": repairs_by_status.get(9, 0),

            # Ingresos
            "revenue": revenue_stats,

            # Alertas
            "alerts": alerts,
            "alerts_count": len(alerts),

            # Timestamp
            "generated_at": now.isoformat()
        }

    def _get_repairs_by_status(self) -> Dict[int, int]:
        """Cuenta reparaciones por estado"""
        results = self.db.query(
            Repair.status_id,
            func.count(Repair.id)
        ).group_by(Repair.status_id).all()

        return {status_id: count for status_id, count in results}

    def _get_revenue_stats(self, start_of_month: datetime) -> Dict[str, Any]:
        """Estadísticas de ingresos"""
        # Total facturado (Invoices PAID)
        total_invoiced = self.db.query(func.sum(Invoice.total)).filter(
            Invoice.status == InvoiceStatus.PAID.value
        ).scalar() or 0

        # Este mes (Invoices PAID)
        invoiced_this_month = self.db.query(func.sum(Invoice.total)).filter(
            Invoice.status == InvoiceStatus.PAID.value,
            Invoice.paid_at >= start_of_month
        ).scalar() or 0

        # Pendiente de cobro
        pending_collection = self.db.query(func.sum(Invoice.amount_due)).filter(
            Invoice.status.in_([InvoiceStatus.SENT.value, InvoiceStatus.VIEWED.value,
                               InvoiceStatus.PARTIAL.value, InvoiceStatus.OVERDUE.value])
        ).scalar() or 0

        # Pagos cobrados reales (Payment.status == success) — refleja dinero real recibido
        # aunque no haya Invoices emitidas
        payments_collected = self.db.query(func.sum(Payment.amount)).filter(
            Payment.status == "success"
        ).scalar() or 0

        payments_this_month = self.db.query(func.sum(Payment.amount)).filter(
            Payment.status == "success",
            Payment.created_at >= start_of_month
        ).scalar() or 0

        return {
            "total_invoiced": total_invoiced,
            "invoiced_this_month": invoiced_this_month,
            "pending_collection": pending_collection,
            "payments_collected": payments_collected,
            "payments_this_month": payments_this_month,
        }

    def _get_alerts(self) -> List[Dict[str, Any]]:
        """Genera alertas del sistema"""
        alerts = []

        # Stock bajo
        low_stock = self.db.query(Stock).filter(
            Stock.quantity <= Stock.minimum_stock
        ).count()
        if low_stock > 0:
            alerts.append({
                "type": "low_stock",
                "severity": "warning",
                "message": f"{low_stock} productos con stock bajo",
                "count": low_stock
            })

        # Facturas vencidas
        overdue_invoices = self.db.query(Invoice).filter(
            Invoice.status == InvoiceStatus.OVERDUE.value
        ).count()
        if overdue_invoices > 0:
            alerts.append({
                "type": "overdue_invoices",
                "severity": "danger",
                "message": f"{overdue_invoices} facturas vencidas",
                "count": overdue_invoices
            })

        # Garantías por expirar (próximos 7 días)
        expiring_warranties = self.db.query(Warranty).filter(
            Warranty.status == WarrantyStatus.ACTIVE.value,
            Warranty.end_date <= datetime.utcnow() + timedelta(days=7),
            Warranty.end_date > datetime.utcnow()
        ).count()
        if expiring_warranties > 0:
            alerts.append({
                "type": "expiring_warranties",
                "severity": "info",
                "message": f"{expiring_warranties} garantías por expirar",
                "count": expiring_warranties
            })

        # Reclamos pendientes
        pending_claims = self.db.query(WarrantyClaim).filter(
            WarrantyClaim.status.in_(["submitted", "under_review"])
        ).count()
        if pending_claims > 0:
            alerts.append({
                "type": "pending_claims",
                "severity": "warning",
                "message": f"{pending_claims} reclamos pendientes",
                "count": pending_claims
            })

        return alerts

    # =========================================================================
    # REPORTES DE REPARACIONES
    # =========================================================================

    def get_repairs_report(
        self,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        status_id: Optional[int] = None,
        technician_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Reporte detallado de reparaciones.
        """
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

        # Calcular métricas
        total_labor = sum(r.labor_cost or 0 for r in repairs)
        total_parts = sum(r.parts_cost or 0 for r in repairs)
        total_quoted = sum(r.quoted_price or 0 for r in repairs)
        total_cost = total_labor + total_parts

        # Por estado
        by_status = defaultdict(int)
        for r in repairs:
            by_status[r.status_id] += 1

        # Por técnico
        by_technician = defaultdict(int)
        for r in repairs:
            if r.assigned_to:
                by_technician[r.assigned_to] += 1

        # Por prioridad
        by_priority = defaultdict(int)
        for r in repairs:
            by_priority[r.priority or 2] += 1

        return {
            "total_repairs": len(repairs),
            "total_labor_cost": total_labor,
            "total_parts_cost": total_parts,
            "total_cost": total_cost,
            "total_quoted": total_quoted,
            "margin": total_quoted - total_cost,
            "margin_percent": round((total_quoted - total_cost) / total_quoted * 100, 2) if total_quoted > 0 else 0,
            "by_status": dict(by_status),
            "by_technician": dict(by_technician),
            "by_priority": dict(by_priority),
            "avg_labor_cost": round(total_labor / len(repairs), 2) if repairs else 0,
            "avg_parts_cost": round(total_parts / len(repairs), 2) if repairs else 0
        }

    def get_repairs_timeline(
        self,
        days: int = 30,
        group_by: str = "day"  # day, week, month
    ) -> List[Dict[str, Any]]:
        """
        Timeline de reparaciones para gráficos.
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        repairs = self.db.query(Repair).filter(
            Repair.created_at >= start_date,
            Repair.created_at <= end_date
        ).all()

        # Agrupar por período
        timeline = defaultdict(lambda: {"created": 0, "completed": 0, "cancelled": 0})

        for repair in repairs:
            if group_by == "day":
                key = repair.created_at.strftime("%Y-%m-%d")
            elif group_by == "week":
                key = repair.created_at.strftime("%Y-W%W")
            else:  # month
                key = repair.created_at.strftime("%Y-%m")

            timeline[key]["created"] += 1
            if repair.status_id in [7, 8]:  # Completado o Entregado
                timeline[key]["completed"] += 1
            elif repair.status_id == 9:  # Cancelado
                timeline[key]["cancelled"] += 1

        # Convertir a lista ordenada
        return [
            {"period": k, **v}
            for k, v in sorted(timeline.items())
        ]

    # =========================================================================
    # REPORTES DE INGRESOS Y FINANZAS
    # =========================================================================

    def get_revenue_report(
        self,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Reporte de ingresos y rentabilidad.
        """
        query = self.db.query(Invoice).filter(
            Invoice.status != InvoiceStatus.VOID.value
        )

        if from_date:
            query = query.filter(Invoice.issue_date >= from_date)
        if to_date:
            query = query.filter(Invoice.issue_date <= to_date)

        invoices = query.all()

        # Totales
        total_invoiced = sum(i.total for i in invoices)
        total_paid = sum(i.amount_paid for i in invoices)
        total_pending = sum(i.amount_due for i in invoices if i.status not in
                          [InvoiceStatus.PAID.value, InvoiceStatus.VOID.value])

        # Por estado
        by_status = defaultdict(lambda: {"count": 0, "total": 0})
        for inv in invoices:
            by_status[inv.status]["count"] += 1
            by_status[inv.status]["total"] += inv.total

        # Por mes
        by_month = defaultdict(lambda: {"invoiced": 0, "paid": 0})
        for inv in invoices:
            month_key = inv.issue_date.strftime("%Y-%m")
            by_month[month_key]["invoiced"] += inv.total
            by_month[month_key]["paid"] += inv.amount_paid

        return {
            "total_invoiced": total_invoiced,
            "total_paid": total_paid,
            "total_pending": total_pending,
            "collection_rate": round(total_paid / total_invoiced * 100, 2) if total_invoiced > 0 else 0,
            "invoice_count": len(invoices),
            "by_status": dict(by_status),
            "by_month": dict(by_month)
        }

    def get_revenue_timeline(
        self,
        months: int = 12
    ) -> List[Dict[str, Any]]:
        """
        Timeline de ingresos por mes.
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=months * 30)

        invoices = self.db.query(Invoice).filter(
            Invoice.issue_date >= start_date,
            Invoice.status != InvoiceStatus.VOID.value
        ).all()

        timeline = defaultdict(lambda: {"invoiced": 0, "paid": 0, "count": 0})

        for inv in invoices:
            month_key = inv.issue_date.strftime("%Y-%m")
            timeline[month_key]["invoiced"] += inv.total
            timeline[month_key]["paid"] += inv.amount_paid
            timeline[month_key]["count"] += 1

        return [
            {"month": k, **v}
            for k, v in sorted(timeline.items())
        ]

    # =========================================================================
    # REPORTES DE CLIENTES
    # =========================================================================

    def get_clients_report(self) -> Dict[str, Any]:
        """
        Reporte de clientes.
        """
        total_clients = self.db.query(func.count(Client.id)).scalar() or 0

        # Clientes este mes
        start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        new_this_month = self.db.query(func.count(Client.id)).filter(
            Client.created_at >= start_of_month
        ).scalar() or 0

        # Por segmento
        by_segment = self.db.query(
            Client.customer_segment,
            func.count(Client.id)
        ).group_by(Client.customer_segment).all()

        # Top clientes por gasto
        top_clients = self.db.query(
            Client.id,
            Client.name,
            Client.total_spent,
            Client.total_repairs
        ).order_by(Client.total_spent.desc()).limit(10).all()

        return {
            "total_clients": total_clients,
            "new_this_month": new_this_month,
            "by_segment": {seg or "regular": count for seg, count in by_segment},
            "top_clients": [
                {"id": c.id, "name": c.name, "total_spent": c.total_spent or 0,
                 "total_repairs": c.total_repairs or 0}
                for c in top_clients
            ]
        }

    # =========================================================================
    # REPORTES DE INVENTARIO
    # =========================================================================

    def get_inventory_report(self) -> Dict[str, Any]:
        """
        Reporte de inventario.
        """
        stocks = self.db.query(Stock).all()

        total_items = len(stocks)
        low_stock_items = sum(1 for s in stocks if s.quantity <= s.minimum_stock)
        out_of_stock = sum(1 for s in stocks if s.quantity == 0)
        total_value = sum((s.unit_cost or 0) * s.quantity for s in stocks)

        # Productos más usados (de RepairComponentUsage)
        most_used = self.db.query(
            RepairComponentUsage.component_id,
            RepairComponentUsage.component_table,
            func.sum(RepairComponentUsage.quantity).label("total_used")
        ).group_by(
            RepairComponentUsage.component_id,
            RepairComponentUsage.component_table
        ).order_by(func.sum(RepairComponentUsage.quantity).desc()).limit(10).all()

        return {
            "total_items": total_items,
            "low_stock_items": low_stock_items,
            "out_of_stock": out_of_stock,
            "total_inventory_value": total_value,
            "most_used_components": [
                {"component_id": m.component_id, "table": m.component_table, "total_used": m.total_used}
                for m in most_used
            ]
        }

    # =========================================================================
    # REPORTES DE TÉCNICOS
    # =========================================================================

    def get_technician_performance(
        self,
        technician_id: Optional[int] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Reporte de productividad de técnicos.
        """
        query = self.db.query(
            User.id,
            User.first_name,
            User.last_name,
            func.count(Repair.id).label("total_repairs"),
            func.sum(case((Repair.status_id.in_([7, 8]), 1), else_=0)).label("completed"),
            func.sum(case((Repair.status_id == 9, 1), else_=0)).label("cancelled"),
            func.avg(Repair.labor_cost).label("avg_labor")
        ).join(Repair, User.id == Repair.assigned_to, isouter=True)

        if technician_id:
            query = query.filter(User.id == technician_id)
        if from_date:
            query = query.filter(Repair.created_at >= from_date)
        if to_date:
            query = query.filter(Repair.created_at <= to_date)

        # Solo técnicos (role_id = 2)
        query = query.filter(User.role_id == 2)
        query = query.group_by(User.id, User.first_name, User.last_name)

        results = query.all()

        return [
            {
                "technician_id": r.id,
                "name": f"{r.first_name or ''} {r.last_name or ''}".strip() or f"User {r.id}",
                "total_repairs": r.total_repairs or 0,
                "completed": r.completed or 0,
                "cancelled": r.cancelled or 0,
                "completion_rate": round((r.completed or 0) / (r.total_repairs or 1) * 100, 2),
                "avg_labor": round(r.avg_labor or 0, 2)
            }
            for r in results
        ]

    # =========================================================================
    # REPORTES DE GARANTÍAS
    # =========================================================================

    def get_warranty_report(self) -> Dict[str, Any]:
        """
        Reporte de garantías.
        """
        total_warranties = self.db.query(func.count(Warranty.id)).scalar() or 0
        active_warranties = self.db.query(func.count(Warranty.id)).filter(
            Warranty.status == WarrantyStatus.ACTIVE.value
        ).scalar() or 0

        # Claims
        total_claims = self.db.query(func.count(WarrantyClaim.id)).scalar() or 0
        approved_claims = self.db.query(func.count(WarrantyClaim.id)).filter(
            WarrantyClaim.status.in_(["approved", "in_progress", "completed"])
        ).scalar() or 0
        rejected_claims = self.db.query(func.count(WarrantyClaim.id)).filter(
            WarrantyClaim.status == "rejected"
        ).scalar() or 0

        # Costo de garantías (claims completados)
        warranty_cost = self.db.query(func.sum(WarrantyClaim.actual_cost)).filter(
            WarrantyClaim.status == "completed"
        ).scalar() or 0

        return {
            "total_warranties": total_warranties,
            "active_warranties": active_warranties,
            "total_claims": total_claims,
            "approved_claims": approved_claims,
            "rejected_claims": rejected_claims,
            "approval_rate": round(approved_claims / total_claims * 100, 2) if total_claims > 0 else 0,
            "total_warranty_cost": warranty_cost
        }

    # =========================================================================
    # KPIs DE TALLER — turnaround, vencidas, conversión, top modelos, retorno
    # =========================================================================

    def get_turnaround_stats(self) -> Dict[str, Any]:
        """
        Tiempo promedio de resolución de OTs (intake_date → completion_date).
        Solo considera OTs completadas o entregadas (status_id 7 u 8).
        """
        completed = self.db.query(Repair).filter(
            Repair.completion_date.isnot(None),
            Repair.intake_date.isnot(None),
            Repair.status_id.in_([7, 8])
        ).all()

        if not completed:
            return {"avg_days": None, "min_days": None, "max_days": None, "count": 0}

        days_list = [
            (r.completion_date - r.intake_date).days
            for r in completed
            if r.completion_date >= r.intake_date
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
        """
        OTs activas (no terminadas ni canceladas) con más de threshold_days días abiertos.
        """
        active_status_ids = [1, 2, 3, 4, 5, 6]
        cutoff = datetime.utcnow() - timedelta(days=threshold_days)

        total_active = self.db.query(func.count(Repair.id)).filter(
            Repair.status_id.in_(active_status_ids)
        ).scalar() or 0

        overdue = self.db.query(func.count(Repair.id)).filter(
            Repair.status_id.in_(active_status_ids),
            Repair.intake_date <= cutoff
        ).scalar() or 0

        return {
            "overdue_count": overdue,
            "threshold_days": threshold_days,
            "total_active": total_active,
            "overdue_pct": round(overdue / total_active * 100, 1) if total_active > 0 else 0,
        }

    def get_lead_conversion(self) -> Dict[str, Any]:
        """
        Tasa de conversión leads → reparaciones.
        Usa el campo status del modelo Lead (new / contacted / converted).
        """
        from app.models.lead import Lead

        total = self.db.query(func.count(Lead.id)).scalar() or 0
        converted = self.db.query(func.count(Lead.id)).filter(
            Lead.status == "converted"
        ).scalar() or 0
        contacted = self.db.query(func.count(Lead.id)).filter(
            Lead.status == "contacted"
        ).scalar() or 0

        return {
            "total_leads": total,
            "new": total - converted - contacted,
            "contacted": contacted,
            "converted": converted,
            "conversion_rate": round(converted / total * 100, 1) if total > 0 else 0,
        }

    def get_top_models(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Modelos de equipos más reparados (join Repair → Device).
        """
        results = self.db.query(
            Device.model,
            func.count(Repair.id).label("repair_count")
        ).join(Repair, Repair.device_id == Device.id)\
         .group_by(Device.model)\
         .order_by(func.count(Repair.id).desc())\
         .limit(limit)\
         .all()

        return [{"model": r.model, "repair_count": r.repair_count} for r in results]

    def get_client_return_rate(self) -> Dict[str, Any]:
        """
        Tasa de retorno de clientes: clientes con más de una OT registrada.
        """
        subq = self.db.query(
            Device.client_id,
            func.count(Repair.id).label("repair_count")
        ).join(Repair, Repair.device_id == Device.id)\
         .group_by(Device.client_id)\
         .subquery()

        total_with_repairs = self.db.query(
            func.count(subq.c.client_id)
        ).scalar() or 0

        returning = self.db.query(
            func.count(subq.c.client_id)
        ).filter(subq.c.repair_count > 1).scalar() or 0

        return {
            "returning_clients": returning,
            "first_time_clients": total_with_repairs - returning,
            "total_clients_with_repairs": total_with_repairs,
            "return_rate": round(returning / total_with_repairs * 100, 1) if total_with_repairs > 0 else 0,
        }

    # =========================================================================
    # EXPORTACIÓN
    # =========================================================================

    def export_repairs_csv(
        self,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Exporta reparaciones para CSV.
        """
        query = self.db.query(Repair)

        if from_date:
            query = query.filter(Repair.created_at >= from_date)
        if to_date:
            query = query.filter(Repair.created_at <= to_date)

        repairs = query.all()

        return [
            {
                "id": r.id,
                "repair_number": r.repair_number,
                "status_id": r.status_id,
                "priority": r.priority,
                "problem_reported": r.problem_reported,
                "diagnosis": r.diagnosis,
                "work_performed": r.work_performed,
                "labor_cost": r.labor_cost,
                "parts_cost": r.parts_cost,
                "quoted_price": r.quoted_price,
                "assigned_to": r.assigned_to,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "updated_at": r.updated_at.isoformat() if r.updated_at else None
            }
            for r in repairs
        ]
