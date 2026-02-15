"""
PHASE 6: Audit Logging Service
Log all critical operations for compliance and security tracking
"""

from datetime import datetime
from typing import Any, Optional, Dict
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class AuditAction(str, Enum):
    """Types of actions to audit"""
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    FAILED_AUTH = "FAILED_AUTH"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    EXPORT_DATA = "EXPORT_DATA"
    IMPORT_DATA = "IMPORT_DATA"


class AuditService:
    """Service to log audit trails for critical operations"""
    
    # In-memory storage (in production, use database)
    logs: list = []
    
    @staticmethod
    def log_action(
        user_id: Optional[int],
        action: AuditAction,
        entity_type: str,
        entity_id: Optional[int],
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        old_values: Optional[Dict] = None,
        new_values: Optional[Dict] = None,
        status: str = "success"
    ) -> Dict[str, Any]:
        """
        Log an audit trail entry
        
        Args:
            user_id: ID of user performing action
            action: Type of action (CREATE, UPDATE, DELETE, etc)
            entity_type: Type of entity (repair, user, category, etc)
            entity_id: ID of entity affected
            details: Additional details/context
            ip_address: IP address of requester
            user_agent: User agent string
            old_values: Values before change (for UPDATE)
            new_values: Values after change (for UPDATE)
            status: "success" or "failure"
        """
        
        timestamp = datetime.utcnow()
        
        # Sanitize sensitive data from logs
        sanitized_old = AuditService._sanitize_values(old_values)
        sanitized_new = AuditService._sanitize_values(new_values)
        
        log_entry = {
            "id": len(AuditService.logs) + 1,
            "timestamp": timestamp.isoformat(),
            "user_id": user_id,
            "action": action.value,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "details": details,
            "old_values": sanitized_old,
            "new_values": sanitized_new,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "status": status
        }
        
        # Store in memory (in production, save to database)
        AuditService.logs.append(log_entry)
        
        # Log to application logger
        log_message = (
            f"[AUDIT] {action.value} {entity_type} "
            f"(id={entity_id}, user={user_id}, status={status})"
        )
        if status == "failure":
            logger.warning(log_message)
        else:
            logger.info(log_message)
        
        return log_entry
    
    @staticmethod
    def _sanitize_values(values: Optional[Dict]) -> Optional[Dict]:
        """Remove sensitive data from logged values"""
        if not values:
            return values
        
        sensitive_fields = {
            'password', 'password_hash', 'ssn', 'credit_card',
            'token', 'api_key', 'secret', 'phone', 'email'
        }
        
        sanitized = {}
        for key, value in values.items():
            if any(sens in key.lower() for sens in sensitive_fields):
                if isinstance(value, str) and len(value) > 4:
                    # Show first and last 2 chars only
                    sanitized[key] = f"{value[:2]}...{value[-2:]}"
                else:
                    sanitized[key] = "***REDACTED***"
            else:
                sanitized[key] = value
        
        return sanitized
    
    @staticmethod
    def log_authentication(
        email: str,
        success: bool,
        ip_address: Optional[str] = None,
        user_id: Optional[int] = None,
        reason: Optional[str] = None
    ):
        """Log authentication attempts"""
        action = AuditAction.LOGIN if success else AuditAction.FAILED_AUTH
        status = "success" if success else "failure"
        
        AuditService.log_action(
            user_id=user_id,
            action=action,
            entity_type="user",
            entity_id=user_id,
            details={
                "email": email,
                "reason": reason
            },
            ip_address=ip_address,
            status=status
        )
    
    @staticmethod
    def log_data_access(
        user_id: int,
        entity_type: str,
        entity_id: int,
        action: str = "VIEW",
        ip_address: Optional[str] = None
    ):
        """Log data access for compliance"""
        AuditService.log_action(
            user_id=user_id,
            action=AuditAction.READ,
            entity_type=entity_type,
            entity_id=entity_id,
            details={"action_type": action},
            ip_address=ip_address
        )
    
    @staticmethod
    def log_permission_denied(
        user_id: int,
        entity_type: str,
        entity_id: int,
        reason: str,
        ip_address: Optional[str] = None
    ):
        """Log permission denied attempts"""
        AuditService.log_action(
            user_id=user_id,
            action=AuditAction.PERMISSION_DENIED,
            entity_type=entity_type,
            entity_id=entity_id,
            details={"reason": reason},
            ip_address=ip_address,
            status="failure"
        )
    
    @staticmethod
    def get_logs(
        user_id: Optional[int] = None,
        action: Optional[AuditAction] = None,
        entity_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> list:
        """Query audit logs with filters"""
        results = AuditService.logs
        
        # Apply filters
        if user_id:
            results = [log for log in results if log["user_id"] == user_id]
        
        if action:
            results = [log for log in results if log["action"] == action.value]
        
        if entity_type:
            results = [log for log in results if log["entity_type"] == entity_type]
        
        if start_date:
            results = [
                log for log in results 
                if datetime.fromisoformat(log["timestamp"]) >= start_date
            ]
        
        if end_date:
            results = [
                log for log in results 
                if datetime.fromisoformat(log["timestamp"]) <= end_date
            ]
        
        # Return most recent first, limited
        return sorted(results, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    @staticmethod
    def export_logs(format: str = "json") -> str:
        """Export logs in specified format"""
        if format == "json":
            return json.dumps(AuditService.logs, indent=2)
        elif format == "csv":
            import csv
            from io import StringIO
            
            output = StringIO()
            if AuditService.logs:
                writer = csv.DictWriter(output, fieldnames=AuditService.logs[0].keys())
                writer.writeheader()
                writer.writerows(AuditService.logs)
            
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    @staticmethod
    def clear_logs():
        """Clear all audit logs (testing only)"""
        AuditService.logs = []


# Decorator for automatic audit logging
def audit_log(
    entity_type: str,
    action: AuditAction,
    get_id_from_response: bool = False
):
    """
    Decorator to automatically log function calls
    
    Usage:
        @audit_log(entity_type="repair", action=AuditAction.CREATE)
        async def create_repair(...):
            ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract request and user info
            request = None
            user_id = None
            entity_id = None
            old_values = None
            new_values = None
            
            # Try to find request object
            for arg in args:
                if hasattr(arg, "client"):  # FastAPI Request
                    request = arg
                    if hasattr(arg.state, "user_id"):
                        user_id = arg.state.user_id
            
            # Extract entity_id from kwargs
            if "id" in kwargs:
                entity_id = kwargs["id"]
            
            # Execute function
            try:
                result = await func(*args, **kwargs)
                
                # Log success
                AuditService.log_action(
                    user_id=user_id,
                    action=action,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    ip_address=request.client.host if request else None,
                    user_agent=request.headers.get("user-agent") if request else None,
                    status="success"
                )
                
                return result
            
            except Exception as e:
                # Log failure
                AuditService.log_action(
                    user_id=user_id,
                    action=action,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    details={"error": str(e)},
                    ip_address=request.client.host if request else None,
                    status="failure"
                )
                raise
        
        return wrapper
    return decorator
