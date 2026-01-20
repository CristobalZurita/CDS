"""
Stats endpoints (API v1)
========================
Estadísticas básicas y KPIs del sistema.
Mejorado para usar ReportingService (ADITIVO).
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_optional_user
from app.models.user import User
from app.models.client import Client
from app.models.repair import Repair
from app.models.inventory import Product

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/")
def get_stats(
    extended: bool = Query(False, description="Incluir estadísticas extendidas"),
    db: Session = Depends(get_db),
    user: Optional[dict] = Depends(get_optional_user)
):
    """
    Estadísticas básicas del sistema.

    Query params:
    - extended: Si es true, incluye KPIs adicionales del ReportingService

    Retorna siempre los contadores básicos para compatibilidad.
    """
    # Contadores básicos (compatibilidad con frontend existente)
    basic_stats = {
        "users": db.query(User).count(),
        "clients": db.query(Client).count(),
        "repairs": db.query(Repair).count(),
        "products": db.query(Product).count()
    }

    # Si no se pide extendido, retornar solo básicos
    if not extended:
        return basic_stats

    # Estadísticas extendidas usando ReportingService
    try:
        from app.services.reporting_service import ReportingService
        svc = ReportingService(db)
        dashboard_stats = svc.get_dashboard_stats()

        # Combinar básicos con extendidos
        return {
            **basic_stats,
            # KPIs de reparaciones
            "repairs_this_month": dashboard_stats.get("repairs_this_month", 0),
            "repairs_by_status": dashboard_stats.get("repairs_by_status", {}),
            "pending_repairs": dashboard_stats.get("pending_repairs", 0),
            "active_repairs": dashboard_stats.get("active_repairs", 0),
            "completed_repairs": dashboard_stats.get("completed_repairs", 0),
            # Ingresos (solo si está autenticado)
            "revenue": dashboard_stats.get("revenue", {}) if user else None,
            # Alertas
            "alerts": dashboard_stats.get("alerts", []),
            "alerts_count": dashboard_stats.get("alerts_count", 0),
            # Meta
            "generated_at": dashboard_stats.get("generated_at")
        }
    except Exception:
        # Si falla ReportingService, retornar básicos
        return basic_stats


@router.get("/quick")
def get_quick_stats(db: Session = Depends(get_db)):
    """
    Estadísticas rápidas (sin autenticación).
    Solo contadores públicos básicos.
    """
    return {
        "repairs": db.query(Repair).count(),
        "clients": db.query(Client).count()
    }


@router.get("/repairs")
def get_repair_stats(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Estadísticas detalladas de reparaciones.
    Requiere autenticación.
    """
    try:
        from app.services.reporting_service import ReportingService
        svc = ReportingService(db)
        return svc.get_repairs_report()
    except Exception as e:
        # Fallback a contadores básicos
        from app.models.repair import RepairStatus
        total = db.query(Repair).count()

        # Contar por estado
        by_status = {}
        for i in range(1, 10):
            count = db.query(Repair).filter(Repair.status_id == i).count()
            if count > 0:
                by_status[i] = count

        return {
            "total_repairs": total,
            "by_status": by_status
        }


@router.get("/dashboard")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Estadísticas completas para el dashboard admin.
    Requiere autenticación.
    """
    try:
        from app.services.reporting_service import ReportingService
        svc = ReportingService(db)
        return svc.get_dashboard_stats()
    except Exception:
        # Fallback
        return {
            "users": db.query(User).count(),
            "clients": db.query(Client).count(),
            "repairs": db.query(Repair).count(),
            "products": db.query(Product).count(),
            "alerts": [],
            "alerts_count": 0
        }
