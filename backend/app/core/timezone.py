"""
TEMPO MAESTRO — Módulo central de zona horaria (ADITIVO)
=========================================================

Este módulo es el RELOJ MAESTRO del sistema. Toda referencia a tiempo
en el backend DEBE usar las funciones de aquí.

Analogía embebidos:
  - Este módulo es el crystal oscillator / PLL del sistema.
  - Genera la frecuencia base (UTC) desde la cual todo se deriva.
  - `now_utc()` es el tick del reloj principal.
  - `to_local()` es el divisor de frecuencia para mostrar al usuario.
  - `ensure_utc()` es el PLL que sincroniza señales externas al master clock.

Regla de oro:
  - La DB almacena SIEMPRE en UTC (timezone-aware).
  - El backend trabaja SIEMPRE en UTC.
  - El frontend recibe UTC y convierte a America/Santiago para mostrar.
  - Cualquier input del usuario se normaliza a UTC al entrar al backend.

Uso:
    from app.core.timezone import now_utc, to_local, ensure_utc, CL_TZ

    # En vez de datetime.utcnow():
    timestamp = now_utc()

    # Para mostrar al usuario chileno:
    local_time = to_local(timestamp)

    # Para normalizar input externo:
    safe_dt = ensure_utc(user_provided_datetime)

NO reemplaza código existente. Los modelos existentes que usan
`datetime.utcnow` siguen funcionando. Este módulo se usa en código
NUEVO y se adopta gradualmente en el existente.
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Optional, Union
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# Constantes de zona horaria
# ============================================================================

# UTC — el master clock
UTC = timezone.utc

# Chile continental (UTC-3 en verano, UTC-4 en invierno)
# Para manejo completo de DST, usar zoneinfo (Python 3.9+)
try:
    from zoneinfo import ZoneInfo
    CL_TZ = ZoneInfo("America/Santiago")
except ImportError:
    # Fallback para Python < 3.9 o sin tzdata
    CL_TZ = timezone(timedelta(hours=-3))
    logger.warning("zoneinfo not available, using fixed UTC-3 offset for Chile")

# Nombre de la zona horaria del negocio (para Google Calendar, emails, etc.)
BUSINESS_TIMEZONE = "America/Santiago"


# ============================================================================
# Funciones del TEMPO MAESTRO
# ============================================================================

def now_utc() -> datetime:
    """
    Retorna el instante actual en UTC, timezone-aware.
    
    REEMPLAZA: datetime.utcnow() (que retorna naive datetime)
    
    Returns:
        datetime con tzinfo=UTC
    
    Ejemplo:
        >>> from app.core.timezone import now_utc
        >>> ts = now_utc()
        >>> ts.tzinfo  # timezone.utc
    """
    return datetime.now(UTC)


def now_local() -> datetime:
    """
    Retorna el instante actual en hora local de Chile.
    
    Uso: Solo para display, emails, PDFs. NUNCA para almacenar en DB.
    
    Returns:
        datetime con tzinfo=America/Santiago
    """
    return datetime.now(CL_TZ)


def to_utc(dt: datetime) -> datetime:
    """
    Convierte un datetime a UTC.
    
    - Si es naive (sin tzinfo): asume que es UTC y le agrega tzinfo.
    - Si tiene tzinfo: convierte a UTC.
    
    Args:
        dt: datetime a convertir
    
    Returns:
        datetime en UTC, timezone-aware
    """
    if dt is None:
        return now_utc()
    
    if dt.tzinfo is None:
        # Naive datetime — asumir UTC (compatible con datetime.utcnow() existente)
        return dt.replace(tzinfo=UTC)
    
    # Ya tiene timezone — convertir a UTC
    return dt.astimezone(UTC)


def to_local(dt: datetime) -> datetime:
    """
    Convierte un datetime UTC a hora local de Chile.
    
    Uso: Para mostrar al usuario en frontend, emails, PDFs.
    
    Args:
        dt: datetime (preferiblemente UTC)
    
    Returns:
        datetime en America/Santiago
    """
    if dt is None:
        return now_local()
    
    if dt.tzinfo is None:
        # Naive — asumir UTC
        dt = dt.replace(tzinfo=UTC)
    
    return dt.astimezone(CL_TZ)


def ensure_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """
    Normaliza cualquier datetime a UTC timezone-aware.
    Seguro para usar con inputs externos (API, formularios, etc.)
    
    - None → None
    - Naive → agrega UTC
    - Aware → convierte a UTC
    
    Args:
        dt: datetime o None
    
    Returns:
        datetime UTC timezone-aware, o None
    """
    if dt is None:
        return None
    return to_utc(dt)


def to_iso(dt: Optional[datetime]) -> Optional[str]:
    """
    Convierte datetime a string ISO 8601 con 'Z' (UTC).
    Formato estándar para APIs REST.
    
    Args:
        dt: datetime o None
    
    Returns:
        String ISO 8601 como "2026-02-22T17:00:00Z", o None
    """
    if dt is None:
        return None
    
    utc_dt = to_utc(dt)
    # Formato con 'Z' explícito para claridad
    return utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def from_iso(iso_string: Optional[str]) -> Optional[datetime]:
    """
    Parsea un string ISO 8601 a datetime UTC timezone-aware.
    Acepta formatos con y sin timezone.
    
    Args:
        iso_string: "2026-02-22T17:00:00Z" o "2026-02-22T17:00:00+00:00"
                   o "2026-02-22T14:00:00-03:00"
    
    Returns:
        datetime en UTC, timezone-aware
    """
    if not iso_string:
        return None
    
    try:
        # Python 3.11+ maneja 'Z' nativo
        if iso_string.endswith('Z'):
            iso_string = iso_string[:-1] + '+00:00'
        
        dt = datetime.fromisoformat(iso_string)
        return to_utc(dt)
    except (ValueError, TypeError):
        logger.warning(f"Could not parse ISO datetime: {iso_string}")
        return None


def format_local(dt: Optional[datetime], fmt: str = "%d/%m/%Y %H:%M") -> str:
    """
    Formatea un datetime para display al usuario chileno.
    
    Args:
        dt: datetime (cualquier timezone)
        fmt: formato strftime (default: DD/MM/YYYY HH:MM)
    
    Returns:
        String formateado en hora local de Chile
    """
    if dt is None:
        return ""
    
    local_dt = to_local(dt)
    return local_dt.strftime(fmt)


# ============================================================================
# Helpers para SQLAlchemy (uso en modelos)
# ============================================================================

def utc_column_default() -> datetime:
    """
    Default para columnas SQLAlchemy nuevas.
    
    Uso en modelos:
        from app.core.timezone import utc_column_default
        created_at = Column(DateTime(timezone=True), default=utc_column_default)
    
    Compatible con el patrón existente `default=datetime.utcnow`
    pero retorna timezone-aware.
    """
    return now_utc()


# ============================================================================
# Constantes para display
# ============================================================================

# Nombres de meses en español (para PDFs, emails)
MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}


def format_local_es(dt: Optional[datetime]) -> str:
    """
    Formatea fecha en español chileno: "22 de Febrero de 2026, 14:00 hrs"
    """
    if dt is None:
        return ""
    
    local_dt = to_local(dt)
    mes = MESES_ES.get(local_dt.month, str(local_dt.month))
    return f"{local_dt.day} de {mes} de {local_dt.year}, {local_dt.strftime('%H:%M')} hrs"
