"""
Decorators de Auditoría - Fase 3 (ADITIVO)
==========================================

Decoradores para auditoría automática de funciones.
Permite agregar logging sin modificar cada función manualmente.

NO reemplaza nada existente - es ADITIVO.

Inspirado en:
- Python decorators
- AOP (Aspect-Oriented Programming)

Uso:
    from app.core.decorators import audit_log, require_permission_decorator
    
    @audit_log(action="repair.create")
    async def create_repair(db, data):
        ...
    
    @require_permission_decorator("repairs", "write")
    async def protected_function(db, user):
        ...
"""

from __future__ import annotations

import functools
import logging
import time
from typing import Any, Callable, Optional, List, Dict

from fastapi import HTTPException, Request, Depends
from starlette.responses import Response


# Logger para auditoría
audit_logger = logging.getLogger("audit.decorators")


# =============================================================================
# Decorador de Auditoría
# =============================================================================
def audit_log(
    action: str,
    entity_type: str = None,
    include_params: bool = True,
    include_result: bool = False
):
    """
    Decorador para auditar automáticamente funciones.
    
    Args:
        action: Tipo de acción (create, update, delete, etc.)
        entity_type: Tipo de entidad (repair, client, etc.)
        include_params: Si True, incluye parámetros en el log
        include_result: Si True, incluye resultado (cuidado con datos sensibles)
    
    Usage:
        @audit_log(action="repair.create", entity_type="repair")
        async def create_repair(db, data):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            params_info = ""
            result_info = ""
            
            # Capturar parámetros (sin datos sensibles)
            if include_params:
                safe_args = _sanitize_args(args, kwargs)
                params_info = f" | args: {safe_args}"
            
            # Log de inicio
            audit_logger.info(
                f"[AUDIT] {action} START | entity: {entity_type or 'unknown'}{params_info}"
            )
            
            try:
                # Ejecutar función
                result = await func(*args, **kwargs)
                
                # Capturar resultado
                if include_result:
                    result_info = f" | result: {_sanitize_result(result)}"
                
                duration = time.time() - start_time
                audit_logger.info(
                    f"[AUDIT] {action} SUCCESS | entity: {entity_type or 'unknown'} | "
                    f"duration: {duration:.3f}s{result_info}"
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                audit_logger.error(
                    f"[AUDIT] {action} FAILED | entity: {entity_type or 'unknown'} | "
                    f"duration: {duration:.3f}s | error: {str(e)}"
                )
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            params_info = ""
            
            if include_params:
                safe_args = _sanitize_args(args, kwargs)
                params_info = f" | args: {safe_args}"
            
            audit_logger.info(
                f"[AUDIT] {action} START | entity: {entity_type or 'unknown'}{params_info}"
            )
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                audit_logger.info(
                    f"[AUDIT] {action} SUCCESS | entity: {entity_type or 'unknown'} | "
                    f"duration: {duration:.3f}s"
                )
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                audit_logger.error(
                    f"[AUDIT] {action} FAILED | entity: {entity_type or 'unknown'} | "
                    f"duration: {duration:.3f}s | error: {str(e)}"
                )
                raise
        
        # Retornar el wrapper apropiado según si es async o sync
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


# =============================================================================
# Decorador de Permisos
# =============================================================================
def require_permission_decorator(
    entity: str,
    action: str = "read"
):
    """
    Decorador para verificar permisos antes de ejecutar una función.
    
    Args:
        entity: Entidad (repairs, clients, inventory, etc.)
        action: Acción (read, write, delete, admin)
    
    Usage:
        @require_permission_decorator("repairs", "write")
        async def create_repair(db, user, data):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Extraer user de args o kwargs
            user = _extract_user(args, kwargs)
            
            if not user:
                raise HTTPException(
                    status_code=401,
                    detail="Authentication required"
                )
            
            # Verificar permisos
            has_permission = _check_permission(user, entity, action)
            
            if not has_permission:
                audit_logger.warning(
                    f"[PERMISSION DENIED] user={user.get('id')} | "
                    f"entity={entity} | action={action}"
                )
                raise HTTPException(
                    status_code=403,
                    detail=f"Permission denied: {action} on {entity}"
                )
            
            audit_logger.info(
                f"[PERMISSION GRANTED] user={user.get('id')} | "
                f"entity={entity} | action={action}"
            )
            
            return await func(*args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            user = _extract_user(args, kwargs)
            
            if not user:
                raise HTTPException(
                    status_code=401,
                    detail="Authentication required"
                )
            
            has_permission = _check_permission(user, entity, action)
            
            if not has_permission:
                audit_logger.warning(
                    f"[PERMISSION DENIED] user={user.get('id')} | "
                    f"entity={entity} | action={action}"
                )
                raise HTTPException(
                    status_code=403,
                    detail=f"Permission denied: {action} on {entity}"
                )
            
            return func(*args, **kwargs)
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


# =============================================================================
# Decorador de Rate Limiting (simplificado)
# =============================================================================
def rate_limit_decorator(
    max_calls: int = 100,
    window_seconds: int = 60
):
    """
    Decorador simple de rate limiting.
    
    Nota: Para producción, usar el middleware de rate limiting existente.
    Este es un ejemplo de cómo aplicar decorators a funciones.
    
    Usage:
        @rate_limit_decorator(max_calls=10, window_seconds=60)
        async def send_notification(db, data):
            ...
    """
    # Almacenamiento en memoria (para demo)
    _call_history: Dict[str, List[float]] = {}
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            import time
            
            # Generar key única
            key = _generate_rate_limit_key(args, kwargs)
            now = time.time()
            
            # Limpiar llamadas antiguas
            if key not in _call_history:
                _call_history[key] = []
            
            _call_history[key] = [
                t for t in _call_history[key]
                if now - t < window_seconds
            ]
            
            # Verificar límite
            if len(_call_history[key]) >= max_calls:
                audit_logger.warning(
                    f"[RATE LIMIT] key={key} | calls={len(_call_history[key])} | "
                    f"limit={max_calls}"
                )
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded: {max_calls} calls per {window_seconds}s"
                )
            
            # Registrar llamada
            _call_history[key].append(now)
            
            return await func(*args, **kwargs)
        
        return async_wrapper
    
    return decorator


# =============================================================================
# Decorador de Cache (memoización)
# =============================================================================
def memoize(ttl_seconds: int = 300):
    """
    Decorador de cache simple para funciones.
    Útil para funciones que llaman a APIs externas o DB frecuentemente.
    
    Usage:
        @memoize(ttl_seconds=60)
        async def get_client_repairs(client_id):
            # Esta función se cacheará por 60 segundos
            ...
    """
    _cache: Dict[str, tuple] = {}
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            import time
            
            # Generar key de cache
            cache_key = _generate_cache_key(func.__name__, args, kwargs)
            now = time.time()
            
            # Verificar si existe en cache y no ha expirado
            if cache_key in _cache:
                cached_time, cached_result = _cache[cache_key]
                if now - cached_time < ttl_seconds:
                    audit_logger.debug(f"[CACHE HIT] {func.__name__}")
                    return cached_result
            
            # Ejecutar y cachear
            result = await func(*args, **kwargs)
            _cache[cache_key] = (now, result)
            
            # Limpiar cache antiguo periódicamente
            if len(_cache) > 1000:
                _cache.clear()
            
            return result
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            import time
            
            cache_key = _generate_cache_key(func.__name__, args, kwargs)
            now = time.time()
            
            if cache_key in _cache:
                cached_time, cached_result = _cache[cache_key]
                if now - cached_time < ttl_seconds:
                    return cached_result
            
            result = func(*args, **kwargs)
            _cache[cache_key] = (now, result)
            
            return result
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


# =============================================================================
# Decorador de Retry
# =============================================================================
def retry_on_failure(
    max_retries: int = 3,
    delay_seconds: float = 1.0,
    exponential_backoff: bool = True
):
    """
    Decorador para reintentar funciones que pueden fallar transientemente.
    
    Usage:
        @retry_on_failure(max_retries=3, delay_seconds=2)
        async def send_to_external_api(data):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            import asyncio
            
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        delay = delay_seconds * (2 ** attempt if exponential_backoff else 1)
                        audit_logger.warning(
                            f"[RETRY] {func.__name__} | attempt={attempt + 1} | "
                            f"error={str(e)} | retrying in {delay}s"
                        )
                        await asyncio.sleep(delay)
            
            audit_logger.error(
                f"[RETRY FAILED] {func.__name__} | attempts={max_retries} | "
                f"error={str(last_exception)}"
            )
            raise last_exception
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            import time
            
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        delay = delay_seconds * (2 ** attempt if exponential_backoff else 1)
                        time.sleep(delay)
            
            raise last_exception
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


# =============================================================================
# Funciones helper
# =============================================================================
def _sanitize_args(args: tuple, kwargs: dict) -> str:
    """Sanitiza argumentos para no exponer datos sensibles"""
    import json
    
    sensitive_keys = {'password', 'token', 'secret', 'api_key', 'hashed_password', 'ssn'}
    
    sanitized = {}
    for k, v in kwargs.items():
        if k.lower() in sensitive_keys:
            sanitized[k] = "***REDACTED***"
        else:
            sanitized[k] = v
    
    try:
        return json.dumps(sanitized, default=str)[:200]
    except:
        return str(sanitized)[:200]


def _sanitize_result(result: Any) -> str:
    """Sanitiza resultado para no exponer datos sensibles"""
    import json
    
    if isinstance(result, dict):
        sensitive_keys = {'password', 'token', 'secret', 'api_key', 'hashed_password'}
        result = {k: v if k.lower() not in sensitive_keys else "***REDACTED***" 
                  for k, v in result.items()}
    
    try:
        return json.dumps(result, default=str)[:200]
    except:
        return str(result)[:200]


def _extract_user(args: tuple, kwargs: dict) -> Optional[dict]:
    """Extrae usuario de argumentos"""
    # Buscar en kwargs
    for key in ['user', 'current_user', 'current_user_obj']:
        if key in kwargs:
            return kwargs[key]
    
    # Buscar en args (usualmente es el segundo argumento después de db)
    if len(args) > 1:
        arg = args[1]
        if isinstance(arg, dict) and 'id' in arg:
            return arg
    
    return None


def _check_permission(user: dict, entity: str, action: str) -> bool:
    """Verifica si el usuario tiene permiso"""
    if not user:
        return False
    
    # Admin tiene todos los permisos
    if user.get('role') == 'admin':
        return True
    
    # Verificar permisos específicos
    permissions = user.get('permissions', {})
    
    # Formato: {entity: [actions]}
    entity_perms = permissions.get(entity, [])
    
    # Admin tiene todos los permisos sobre la entidad
    if 'admin' in entity_perms:
        return True
    
    # Verificar acción específica
    return action in entity_perms


def _generate_rate_limit_key(args: tuple, kwargs: dict) -> str:
    """Genera key única para rate limiting"""
    user = _extract_user(args, kwargs)
    if user:
        return f"user_{user.get('id')}"
    return f"ip_{kwargs.get('request', {}).get('client', {}).get('host', 'unknown')}"


def _generate_cache_key(func_name: str, args: tuple, kwargs: dict) -> str:
    """Genera key única para cache"""
    import json
    return f"{func_name}:{json.dumps(args, default=str)}:{json.dumps(kwargs, default=str)}"


# =============================================================================
# Decorador de Validación de Entrada
# =============================================================================
def validate_input(**validators):
    """
    Decorador para validar argumentos de entrada.
    
    Usage:
        @validate_input(
            client_id=lambda x: x > 0,
            email=lambda x: '@' in x
        )
        async def update_client(db, client_id, email):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            for field, validator in validators.items():
                value = kwargs.get(field) or (args[args.index(field)] if field in args else None)
                if value is not None and not validator(value):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Validation failed for {field}"
                    )
            return await func(*args, **kwargs)
        
        return async_wrapper
    
    return decorator


# =============================================================================
# Ejemplo de uso (documentación)
# =============================================================================
"""
# EJEMPLO 1: Auditoría básica
from app.core.decorators import audit_log

@audit_log(action="repair.create", entity_type="repair")
async def create_repair(db, data):
    repair = Repair(...)
    db.add(repair)
    db.commit()
    return repair


# EJEMPLO 2: Con permisos
from app.core.decorators import require_permission_decorator

@require_permission_decorator("repairs", "write")
async def update_repair_status(db, user, repair_id, new_status):
    # user ya viene validado por el decorador
    ...


# EJEMPLO 3: Retry con exponential backoff
from app.core.decorators import retry_on_failure

@retry_on_failure(max_retries=3, delay_seconds=2, exponential_backoff=True)
async def send_whatsapp_message(phone, message):
    # Puede fallar transientemente
    ...


# EJEMPLO 4: Cache para funciones frecuentes
from app.core.decorators import memoize

@memoize(ttl_seconds=60)
async def get_client_stats(client_id):
    # Se cacheará por 60 segundos
    return await expensive_db_query(client_id)


# EJEMPLO 5: Combinando decoradores
@audit_log(action="inventory.update", entity_type="inventory")
@require_permission_decorator("inventory", "write")
@memoize(ttl_seconds=30)
async def update_inventory_stock(db, user, product_id, quantity):
    ...
"""
