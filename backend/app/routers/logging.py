"""
PHASE 8: Observability - Logging Endpoint
Receive logs from frontend and store for analysis
"""

from fastapi import APIRouter, Request, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogEntry(BaseModel):
    timestamp: str
    level: LogLevel
    message: str
    context: Optional[dict] = None
    stackTrace: Optional[str] = None
    url: Optional[str] = None
    userAgent: Optional[str] = None
    userId: Optional[int] = None


class PerformanceMetric(BaseModel):
    name: str
    duration: float
    timestamp: str
    metadata: Optional[dict] = None


class LoggingService:
    """Service to collect and analyze logs from frontend"""
    
    logs: List[LogEntry] = []
    metrics: List[PerformanceMetric] = []
    max_logs = 10000
    max_metrics = 5000
    
    @classmethod
    def add_log(cls, entry: LogEntry) -> None:
        """Add log entry"""
        cls.logs.append(entry)
        if len(cls.logs) > cls.max_logs:
            cls.logs.pop(0)
        
        # Log critical errors to backend logger
        if entry.level in [LogLevel.ERROR, LogLevel.CRITICAL]:
            logger.error(f"Frontend {entry.level}: {entry.message}", extra={
                "context": entry.context,
                "url": entry.url,
                "stackTrace": entry.stackTrace
            })
    
    @classmethod
    def add_metric(cls, metric: PerformanceMetric) -> None:
        """Add performance metric"""
        cls.metrics.append(metric)
        if len(cls.metrics) > cls.max_metrics:
            cls.metrics.pop(0)
        
        # Alert on slow operations (>2s)
        if metric.duration > 2000:
            logger.warning(f"Slow operation: {metric.name} took {metric.duration}ms")
    
    @classmethod
    def get_logs(cls, level: Optional[LogLevel] = None, limit: int = 100) -> List[LogEntry]:
        """Get logs, optionally filtered by level"""
        filtered = cls.logs
        if level:
            filtered = [l for l in filtered if l.level == level]
        return filtered[-limit:]
    
    @classmethod
    def get_metrics(cls, name: Optional[str] = None, limit: int = 100) -> List[PerformanceMetric]:
        """Get metrics, optionally filtered by name"""
        filtered = cls.metrics
        if name:
            filtered = [m for m in filtered if name in m.name]
        return filtered[-limit:]
    
    @classmethod
    def get_stats(cls) -> dict:
        """Get logging statistics"""
        error_count = len([l for l in cls.logs if l.level == LogLevel.ERROR])
        critical_count = len([l for l in cls.logs if l.level == LogLevel.CRITICAL])
        
        avg_duration = 0
        if cls.metrics:
            avg_duration = sum(m.duration for m in cls.metrics) / len(cls.metrics)
        
        slow_operations = len([m for m in cls.metrics if m.duration > 2000])
        
        return {
            "total_logs": len(cls.logs),
            "error_count": error_count,
            "critical_count": critical_count,
            "total_metrics": len(cls.metrics),
            "avg_duration_ms": avg_duration,
            "slow_operations": slow_operations
        }
    
    @classmethod
    def clear_logs(cls) -> None:
        """Clear all logs"""
        cls.logs.clear()
    
    @classmethod
    def clear_metrics(cls) -> None:
        """Clear all metrics"""
        cls.metrics.clear()


router = APIRouter(prefix="/api", tags=["logging"])


@router.post("/logs")
async def log_event(entry: LogEntry, request: Request):
    """Receive log event from frontend"""
    try:
        # Add client IP
        entry.context = entry.context or {}
        entry.context["client_ip"] = request.client.host if request.client else "unknown"
        
        LoggingService.add_log(entry)
        logger.debug(f"Log received: {entry.level} - {entry.message}")
        
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error processing log: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/metrics")
async def log_metric(metric: PerformanceMetric):
    """Receive performance metric from frontend"""
    try:
        LoggingService.add_metric(metric)
        logger.debug(f"Metric received: {metric.name} - {metric.duration}ms")
        
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error processing metric: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/logs")
async def get_logs(level: Optional[LogLevel] = None, limit: int = 100):
    """Get logs from backend storage"""
    logs = LoggingService.get_logs(level, limit)
    return {"count": len(logs), "logs": logs}


@router.get("/metrics")
async def get_metrics(name: Optional[str] = None, limit: int = 100):
    """Get performance metrics"""
    metrics = LoggingService.get_metrics(name, limit)
    return {"count": len(metrics), "metrics": metrics}


@router.get("/logs/stats")
async def get_log_stats():
    """Get logging statistics"""
    return LoggingService.get_stats()


@router.delete("/logs")
async def clear_logs():
    """Clear all logs"""
    LoggingService.clear_logs()
    return {"status": "cleared"}


@router.delete("/metrics")
async def clear_metrics():
    """Clear all metrics"""
    LoggingService.clear_metrics()
    return {"status": "cleared"}
