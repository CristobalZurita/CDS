"""
PHASE 3: Backend Security Wiring - Validation Middleware
Wire validators.py, encryption.py, sanitizers.py to all 165 endpoints
"""

from fastapi import Request, HTTPException, status
from typing import Any, Callable, Dict, Optional
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ValidationRules:
    """Central registry of validation rules for all endpoints"""
    
    # Patrones de SQL injection
    SQL_INJECTION_PATTERNS = [
        r"(\bUNION\b.*\bSELECT\b)",
        r"(\bOR\b\s*['\"]?\d+['\"]?\s*=)",
        r"(--\s*$)",  # SQL comment
        r"(/\*.*?\*/)",  # Block comment
        r"(;\s*DROP)",
        r"(;\s*DELETE)",
        r"(xp_cmdshell)",
        r"(exec\s*\()",
        r"(execute\s*\()",
    ]
    
    # Patrones XSS
    XSS_PATTERNS = [
        r"<script[^>]*>",
        r"<iframe[^>]*>",
        r"<embed[^>]*>",
        r"<object[^>]*>",
        r"javascript:",
        r"on\w+\s*=",
    ]
    
    @staticmethod
    def check_sql_injection(value: str) -> bool:
        """Detecta patrones SQL injection"""
        if not isinstance(value, str):
            return False
        
        for pattern in ValidationRules.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE | re.MULTILINE):
                return True
        return False
    
    @staticmethod
    def check_xss(value: str) -> bool:
        """Detecta patrones XSS"""
        if not isinstance(value, str):
            return False
        
        for pattern in ValidationRules.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False
    
    @staticmethod
    def validate_email(email: str) -> str:
        """Valida email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email.strip()):
            raise ValueError("Invalid email format")
        return email.lower().strip()
    
    @staticmethod
    def validate_string(value: str, field_name: str, min_length: int = 1, max_length: int = 1000) -> str:
        """Valida string sin inyección"""
        if not isinstance(value, str):
            raise ValueError(f"{field_name} must be string")
        
        value = value.strip()
        
        # Verificar longitud
        if len(value) < min_length:
            raise ValueError(f"{field_name} too short (min: {min_length})")
        if len(value) > max_length:
            raise ValueError(f"{field_name} too long (max: {max_length})")
        
        # Verificar SQL injection
        if ValidationRules.check_sql_injection(value):
            raise ValueError(f"{field_name} contains SQL injection patterns")
        
        # Verificar XSS
        if ValidationRules.check_xss(value):
            raise ValueError(f"{field_name} contains XSS patterns")
        
        return value
    
    @staticmethod
    def validate_phone(phone: str) -> str:
        """Valida número telefónico"""
        # Remover caracteres no numéricos excepto + y -
        cleaned = re.sub(r'[^\d+\-\s]', '', phone)
        
        # Validar que tenga al menos 7 dígitos
        digits = re.sub(r'\D', '', cleaned)
        if len(digits) < 7:
            raise ValueError("Invalid phone number")
        
        if len(digits) > 15:
            raise ValueError("Phone number too long")
        
        return cleaned
    
    @staticmethod
    def validate_url(url: str) -> str:
        """Valida URL"""
        try:
            from urllib.parse import urlparse
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                raise ValueError("Invalid URL format")
            if result.scheme not in ['http', 'https']:
                raise ValueError("Only HTTP and HTTPS allowed")
            return url
        except Exception as e:
            raise ValueError(f"Invalid URL: {str(e)}")
    
    @staticmethod
    def validate_integer(value: Any, field_name: str, min_val: Optional[int] = None, max_val: Optional[int] = None) -> int:
        """Valida integer"""
        try:
            num = int(value)
        except (ValueError, TypeError):
            raise ValueError(f"{field_name} must be integer")
        
        if min_val is not None and num < min_val:
            raise ValueError(f"{field_name} below minimum ({min_val})")
        if max_val is not None and num > max_val:
            raise ValueError(f"{field_name} above maximum ({max_val})")
        
        return num
    
    @staticmethod
    def validate_enum(value: str, field_name: str, allowed_values: list) -> str:
        """Valida enum"""
        if value not in allowed_values:
            raise ValueError(f"{field_name} must be one of: {', '.join(allowed_values)}")
        return value
    
    @staticmethod
    def validate_decimal(value: Any, field_name: str, min_val: Optional[float] = None, max_val: Optional[float] = None) -> float:
        """Valida número decimal"""
        try:
            num = float(value)
        except (ValueError, TypeError):
            raise ValueError(f"{field_name} must be number")
        
        if min_val is not None and num < min_val:
            raise ValueError(f"{field_name} below minimum ({min_val})")
        if max_val is not None and num > max_val:
            raise ValueError(f"{field_name} above maximum ({max_val})")
        
        return num
    
    @staticmethod
    def validate_date_iso(value: str) -> datetime:
        """Valida fecha en formato ISO"""
        try:
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            raise ValueError("Invalid ISO date format")


# Mapping de reglas de validación por endpoint
ENDPOINT_VALIDATION_RULES = {
    "POST /api/repairs": {
        "patient_name": lambda v: ValidationRules.validate_string(v, "patient_name", min_length=2, max_length=255),
        "email": lambda v: ValidationRules.validate_email(v),
        "diagnosis": lambda v: ValidationRules.validate_string(v, "diagnosis", min_length=5, max_length=2000),
        "symptoms": lambda v: [ValidationRules.validate_string(s, "symptom", min_length=2, max_length=100) for s in v] if isinstance(v, list) else v,
        "notes": lambda v: ValidationRules.validate_string(v, "notes", max_length=5000) if v else None,
    },
    "PUT /api/repairs/{id}": {
        "status": lambda v: ValidationRules.validate_enum(v, "status", ["pending", "in_progress", "completed", "archived"]),
        "diagnosis": lambda v: ValidationRules.validate_string(v, "diagnosis", min_length=5, max_length=2000) if v else None,
    },
    "POST /api/users": {
        "email": lambda v: ValidationRules.validate_email(v),
        "name": lambda v: ValidationRules.validate_string(v, "name", min_length=2, max_length=255),
        "phone": lambda v: ValidationRules.validate_phone(v) if v else None,
        "password": lambda v: ValidationRules.validate_string(v, "password", min_length=12, max_length=255),
    },
    "POST /api/categories": {
        "name": lambda v: ValidationRules.validate_string(v, "name", min_length=2, max_length=255),
        "description": lambda v: ValidationRules.validate_string(v, "description", max_length=1000) if v else None,
    },
    "POST /api/appointments": {
        "scheduled_at": lambda v: ValidationRules.validate_date_iso(v),
        "status": lambda v: ValidationRules.validate_enum(v, "status", ["scheduled", "completed", "cancelled"]),
    },
    "POST /api/invoices": {
        "amount": lambda v: ValidationRules.validate_decimal(v, "amount", min_val=0, max_val=999999.99),
        "status": lambda v: ValidationRules.validate_enum(v, "status", ["draft", "sent", "paid", "overdue"]),
    },
}


class ValidationMiddleware:
    """Middleware para validar inputs en todos los endpoints"""
    
    @staticmethod
    async def validate_endpoint_input(request: Request, call_next: Callable) -> Any:
        """Middleware que valida inputs según reglas del endpoint"""
        
        # Obtener endpoint key
        method = request.method
        path = request.url.path
        endpoint_key = f"{method} {path}"
        
        # Verificar si hay reglas para este endpoint
        if endpoint_key in ENDPOINT_VALIDATION_RULES:
            try:
                # Obtener body
                if method in ["POST", "PUT", "PATCH"]:
                    body = await request.json()
                    rules = ENDPOINT_VALIDATION_RULES[endpoint_key]
                    
                    # Validar cada campo
                    for field, validator in rules.items():
                        if field in body:
                            try:
                                body[field] = validator(body[field])
                            except ValueError as e:
                                logger.warning(f"Validation failed for {endpoint_key}.{field}: {str(e)}")
                                raise HTTPException(
                                    status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"Invalid {field}: {str(e)}"
                                )
                        elif field.endswith("*"):  # Campo obligatorio
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Missing required field: {field}"
                            )
                    
                    # Re-set body in request
                    async def receive():
                        return {"type": "http.request", "body": str(body).encode()}
                    
                    request._receive = receive
                    
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Validation error on {endpoint_key}: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid request data"
                )
        
        # Continuar con siguiente middleware/handler
        response = await call_next(request)
        return response


# Decorator para aplicar validación a endpoints específicos
def validate_input(validation_rules: Dict[str, Callable]):
    """Decorator para validar inputs en un endpoint específico"""
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            # Obtener request del contexto
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if request:
                body = await request.json()
                
                # Aplicar validaciones
                for field, validator in validation_rules.items():
                    if field in body:
                        try:
                            body[field] = validator(body[field])
                        except ValueError as e:
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Invalid {field}: {str(e)}"
                            )
                
                # Actualizar request
                kwargs['body'] = body
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator
