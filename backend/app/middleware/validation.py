"""
PHASE 3: Backend Security Wiring - Validation Middleware
Wire validators.py, encryption.py, sanitizers.py to all 165 endpoints
"""

import json
import logging
import re
from datetime import datetime
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Any, Callable, Dict, Optional

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


class ValidationMiddleware(BaseHTTPMiddleware):
    """Middleware para validar inputs en todos los endpoints"""

    _PATH_PARAM_PATTERN = re.compile(r"\{[^/]+\}")

    @staticmethod
    def _candidate_endpoint_keys(method: str, path: str) -> list[str]:
        """
        Mantiene compatibilidad con reglas legacy (/api/...) y rutas reales (/api/v1/...).
        """
        candidates = [f"{method} {path}"]
        if path.startswith("/api/v1/"):
            candidates.append(f"{method} {path.replace('/api/v1/', '/api/', 1)}")
        elif path == "/api/v1":
            candidates.append(f"{method} /api")
        return candidates

    @classmethod
    def _resolve_validation_rules(cls, method: str, path: str) -> tuple[str, Dict[str, Callable]] | tuple[None, None]:
        candidates = cls._candidate_endpoint_keys(method, path)

        # Exact match first
        for endpoint_key in candidates:
            if endpoint_key in ENDPOINT_VALIDATION_RULES:
                return endpoint_key, ENDPOINT_VALIDATION_RULES[endpoint_key]

        # Pattern fallback for keys like /resource/{id}
        for endpoint_key, rules in ENDPOINT_VALIDATION_RULES.items():
            for candidate in candidates:
                method_expected, route_expected = endpoint_key.split(" ", 1)
                method_candidate, route_candidate = candidate.split(" ", 1)
                if method_expected != method_candidate:
                    continue
                pattern = "^" + cls._PATH_PARAM_PATTERN.sub(r"[^/]+", route_expected).replace("*", ".*") + "$"
                if re.match(pattern, route_candidate):
                    return candidate, rules

        return None, None

    @staticmethod
    async def _inject_json_body(request: Request, body: Dict[str, Any]) -> None:
        raw = json.dumps(body).encode("utf-8")

        async def receive():
            return {"type": "http.request", "body": raw, "more_body": False}

        request._receive = receive

    async def dispatch(self, request: Request, call_next: Callable) -> Any:
        method = request.method
        if method not in ("POST", "PUT", "PATCH"):
            return await call_next(request)

        endpoint_key, rules = self._resolve_validation_rules(method, request.url.path)
        if not rules:
            return await call_next(request)

        try:
            body = await request.json()
            if not isinstance(body, dict):
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"detail": "Invalid request data"},
                )

            for field, validator in rules.items():
                if field in body:
                    try:
                        body[field] = validator(body[field])
                    except ValueError as exc:
                        logger.warning("Validation failed for %s.%s: %s", endpoint_key, field, str(exc))
                        return JSONResponse(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            content={"detail": f"Invalid {field}: {str(exc)}"},
                        )
                elif field.endswith("*"):  # Campo obligatorio
                    return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={"detail": f"Missing required field: {field}"},
                    )

            await self._inject_json_body(request, body)
        except Exception as exc:
            logger.error("Validation error on %s: %s", endpoint_key, str(exc))
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Invalid request data"},
            )

        return await call_next(request)


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
