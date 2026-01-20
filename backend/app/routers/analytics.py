"""
Router de Analytics y Reportes
==============================
Endpoints para KPIs, estadísticas y reportes del dashboard.
ADITIVO: Nuevo router, no modifica existentes.
Usa permisos granulares (require_permission).
"""
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import csv
import io

from app.core.database import get_db
from app.core.dependencies import (
    get_current_user,
    get_current_admin,
    require_permission
)
from app.services.reporting_service import ReportingService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


# ============================================================================
# DASHBOARD PRINCIPAL
# ============================================================================

@router.get("/dashboard")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("reports", "read"))
):
    """
    Estadísticas principales del dashboard.

    Retorna:
    - Contadores (users, clients, repairs)
    - Reparaciones por estado
    - KPIs de ingresos
    - Alertas del sistema
    """
    svc = ReportingService(db)
    return svc.get_dashboard_stats()


@router.get("/alerts")
def get_system_alerts(
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("reports", "read"))
):
    """Obtener solo las alertas del sistema"""
    svc = ReportingService(db)
    stats = svc.get_dashboard_stats()
    return {
        "alerts": stats["alerts"],
        "count": stats["alerts_count"]
    }


# ============================================================================
# REPORTES DE REPARACIONES
# ============================================================================

@router.get("/repairs")
def get_repairs_report(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    status_id: Optional[int] = None,
    technician_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("reports", "read"))
):
    """
    Reporte detallado de reparaciones.

    Query params:
    - from_date: Fecha desde (ISO format)
    - to_date: Fecha hasta (ISO format)
    - status_id: Filtrar por estado
    - technician_id: Filtrar por técnico
    """
    svc = ReportingService(db)

    from_dt = datetime.fromisoformat(from_date) if from_date else None
    to_dt = datetime.fromisoformat(to_date) if to_date else None

    return svc.get_repairs_report(
        from_date=from_dt,
        to_date=to_dt,
        status_id=status_id,
        technician_id=technician_id
    )


@router.get("/repairs/timeline")
def get_repairs_timeline(
    days: int = Query(30, ge=1, le=365),
    group_by: str = Query("day", regex="^(day|week|month)$"),
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("reports", "read"))
):
    """
    Timeline de reparaciones para gráficos.

    Query params:
    - days: Número de días a consultar (default: 30)
    - group_by: Agrupación (day, week, month)
    """
    svc = ReportingService(db)
    return svc.get_repairs_timeline(days=days, group_by=group_by)


@router.get("/repairs/export")
def export_repairs_csv(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("reports", "export"))
):
    """
    Exportar reparaciones a CSV (requiere permiso reports:export).
    """
    svc = ReportingService(db)

    from_dt = datetime.fromisoformat(from_date) if from_date else None
    to_dt = datetime.fromisoformat(to_date) if to_date else None

    data = svc.export_repairs_csv(from_date=from_dt, to_date=to_dt)

    # Generar CSV
    output = io.StringIO()
    if data:
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

    output.seek(0)

    filename = f"repairs_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# ============================================================================
# REPORTES DE INGRESOS
# ============================================================================

@router.get("/revenue")
def get_revenue_report(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("reports", "read"))
):
    """
    Reporte de ingresos y rentabilidad (solo admin).

    Query params:
    - from_date: Fecha desde (ISO format)
    - to_date: Fecha hasta (ISO format)
    """
    svc = ReportingService(db)

    from_dt = datetime.fromisoformat(from_date) if from_date else None
    to_dt = datetime.fromisoformat(to_date) if to_date else None

    return svc.get_revenue_report(from_date=from_dt, to_date=to_dt)


@router.get("/revenue/timeline")
def get_revenue_timeline(
    months: int = Query(12, ge=1, le=24),
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("reports", "read"))
):
    """
    Timeline de ingresos por mes (solo admin).

    Query params:
    - months: Número de meses a consultar (default: 12)
    """
    svc = ReportingService(db)
    return svc.get_revenue_timeline(months=months)


# ============================================================================
# REPORTES DE CLIENTES
# ============================================================================

@router.get("/clients")
def get_clients_report(
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("reports", "read"))
):
    """
    Reporte de clientes.

    Retorna:
    - Total de clientes
    - Nuevos este mes
    - Por segmento
    - Top clientes por gasto
    """
    svc = ReportingService(db)
    return svc.get_clients_report()


# ============================================================================
# REPORTES DE INVENTARIO
# ============================================================================

@router.get("/inventory")
def get_inventory_report(
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("reports", "read"))
):
    """
    Reporte de inventario.

    Retorna:
    - Total de items
    - Stock bajo
    - Sin stock
    - Valor del inventario
    - Componentes más usados
    """
    svc = ReportingService(db)
    return svc.get_inventory_report()


# ============================================================================
# REPORTES DE TÉCNICOS
# ============================================================================

@router.get("/technicians")
def get_technician_performance(
    technician_id: Optional[int] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("reports", "read"))
):
    """
    Reporte de productividad de técnicos (solo admin).

    Query params:
    - technician_id: Filtrar por técnico específico
    - from_date: Fecha desde
    - to_date: Fecha hasta
    """
    svc = ReportingService(db)

    from_dt = datetime.fromisoformat(from_date) if from_date else None
    to_dt = datetime.fromisoformat(to_date) if to_date else None

    return svc.get_technician_performance(
        technician_id=technician_id,
        from_date=from_dt,
        to_date=to_dt
    )


# ============================================================================
# REPORTES DE GARANTÍAS
# ============================================================================

@router.get("/warranties")
def get_warranty_report(
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("reports", "read"))
):
    """
    Reporte de garantías.

    Retorna:
    - Total de garantías
    - Activas
    - Claims (total, aprobados, rechazados)
    - Tasa de aprobación
    - Costo total de garantías
    """
    svc = ReportingService(db)
    return svc.get_warranty_report()


# ============================================================================
# KPIs COMBINADOS (para widgets del dashboard)
# ============================================================================

@router.get("/kpis/summary")
def get_kpis_summary(
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("reports", "read"))
):
    """
    Resumen de KPIs principales (solo admin).
    Combina métricas de diferentes reportes.
    """
    svc = ReportingService(db)

    dashboard = svc.get_dashboard_stats()
    clients = svc.get_clients_report()
    inventory = svc.get_inventory_report()
    warranty = svc.get_warranty_report()

    return {
        # Reparaciones
        "total_repairs": dashboard["repairs"],
        "active_repairs": dashboard["active_repairs"],
        "repairs_this_month": dashboard["repairs_this_month"],

        # Clientes
        "total_clients": clients["total_clients"],
        "new_clients_this_month": clients["new_this_month"],

        # Ingresos
        "revenue": dashboard["revenue"],

        # Inventario
        "low_stock_alerts": inventory["low_stock_items"],
        "out_of_stock": inventory["out_of_stock"],
        "inventory_value": inventory["total_inventory_value"],

        # Garantías
        "active_warranties": warranty["active_warranties"],
        "pending_claims": warranty["total_claims"] - warranty["approved_claims"] - warranty["rejected_claims"],

        # Alertas
        "alerts": dashboard["alerts"],

        # Meta
        "generated_at": dashboard["generated_at"]
    }
