"""
Cirujano de Sintetizadores - Backend API
Sistema integral de gestión para taller de reparación de sintetizadores

FastAPI application with async database support, JWT authentication,
and comprehensive diagnostic/quotation system.
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager, suppress
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.security import verify_crypto_dependencies
from app.core.database import init_db, close_db
from app.api.v1.router import api_router
from app.core.ratelimit import limiter
from slowapi.errors import RateLimitExceeded
from app.routers import csrf as csrf_router
from app.routers.csrf import validate_csrf_token
from app.routers import logging as logging_router
from app.middleware.validation import ValidationMiddleware


async def _rate_limit_exceeded_handler(request, exc):
    return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Lifespan context manager for app startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("🚀 Application startup")
    instrument_sync_task = None
    # Verify cryptographic dependencies early (fail-fast)
    verify_crypto_dependencies()
    # Setup structured logging early
    try:
        from app.core.logging_config import setup_logging
        setup_logging()
    except Exception as e:
        logger.warning(f"Could not configure structured logging: {e}")
    
    # Initialize event system
    try:
        from app.services.event_handlers import setup_event_handlers
        setup_event_handlers()
        logger.info("✓ Event system initialized")
    except Exception as e:
        logger.error(f"✗ Event system initialization failed: {e}")
    
    try:
        await init_db()
        logger.info("✓ Database initialized")
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {e}")

    # Auto-sync instrumentos: startup + intervalo periódico
    is_test_env = settings.environment and settings.environment.lower() in ("test", "testing")
    if settings.enable_instrument_auto_sync and not is_test_env:
        try:
            from app.services.instrument_sync_service import run_instrument_sync

            if settings.instrument_sync_on_startup:
                await asyncio.to_thread(run_instrument_sync, False, 120, "startup")
                logger.info("✓ Instrument sync ejecutado en startup")

            interval_minutes = max(5, int(settings.instrument_sync_interval_minutes))

            async def _periodic_instrument_sync():
                while True:
                    await asyncio.sleep(interval_minutes * 60)
                    await asyncio.to_thread(run_instrument_sync, False, 120, "periodic")

            instrument_sync_task = asyncio.create_task(_periodic_instrument_sync())
            logger.info(f"✓ Instrument auto-sync periódico activo cada {interval_minutes} minutos")
        except Exception as e:
            logger.error(f"✗ Instrument auto-sync initialization failed: {e}")
    elif is_test_env:
        logger.info("ℹ️ Instrument auto-sync deshabilitado en entorno de testing")

    # Attempt to import and register any routers that may have failed to import at module load
    try:
        import importlib
        from app.api.v1 import router as v1router
        for mod_name in ("backend.app.routers.diagnostic", "backend.app.routers.payments"):
            try:
                mod = importlib.import_module(mod_name)
                if hasattr(mod, "router"):
                    # Avoid double-registration by checking for an existing path
                    prefix = getattr(mod.router, "prefix", "")
                    exists = any(r.path.startswith(f"{v1router.api_router.prefix}{prefix}") for r in app.routes)
                    if not exists:
                        v1router.api_router.include_router(mod.router)
                        logger.info(f"Included router from {mod_name}")
            except Exception:
                # Non-fatal: continue if router import fails in trimmed test envs
                logger.debug(f"Router {mod_name} not available at startup")
    except Exception:
        logger.debug("Dynamic router registration skipped")
    
    yield
    
    # Shutdown logic
    logger.info("🛑 Application shutdown")
    if instrument_sync_task:
        instrument_sync_task.cancel()
        with suppress(asyncio.CancelledError):
            await instrument_sync_task

    try:
        await close_db()
        logger.info("✓ Database connection closed")
    except Exception as e:
        logger.error(f"✗ Error during shutdown: {e}")


@asynccontextmanager
async def _testing_lifespan(app: FastAPI):
    """
    Lifespan reducido para tests.
    Evita bloqueos de TestClient por inicializaciones pesadas y asume que tests
    preparan schema/datos vía fixtures o setup explícito.
    """
    logger.info("🧪 Test lifespan activo (startup pesado omitido)")
    yield


# Initialize FastAPI app
_is_test_env = settings.environment and settings.environment.lower() in ("test", "testing")
_use_light_test_lifespan = _is_test_env and os.getenv("ENABLE_FULL_STARTUP_IN_TESTS", "false").lower() != "true"
app = FastAPI(
    title="Cirujano de Sintetizadores API",
    description="Sistema integral de gestión para taller de reparación de sintetizadores",
    version="1.0.0",
    lifespan=_testing_lifespan if _use_light_test_lifespan else lifespan,
    docs_url="/docs" if settings.enable_api_docs else None,
    redoc_url="/redoc" if settings.enable_api_docs else None,
    openapi_url="/openapi.json" if settings.enable_api_docs else None,
    redirect_slashes=False
)

# Configure CORS with settings
allowed_origins = list(settings.allowed_origins or [])
if settings.environment and settings.environment.lower() in ("development", "dev"):
    for origin in ("http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173", "http://127.0.0.1:5174"):
        if origin not in allowed_origins:
            allowed_origins.append(origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"CORS configured for origins: {allowed_origins}")

# Add security middlewares
app.add_middleware(ValidationMiddleware)
# Rate limiter registration should be available in all environments
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Enforce HTTPS and add basic security headers when running in production
if settings.environment and settings.environment.lower() in ("production", "prod"):
    # Redirect HTTP to HTTPS
    app.add_middleware(HTTPSRedirectMiddleware)

    @app.middleware("http")
    async def add_security_headers(request, call_next):
        response = await call_next(request)
        # HSTS: 2 years, include subdomains, preload
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer-when-downgrade"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=()"
        return response

    # Expose audit service for internal use
    try:
        from app.services import logging_service  # noqa: F401
    except Exception:
        # Import failures are non-fatal; logging service may not be available in trimmed test envs
        pass

# Include API v1 routes
app.include_router(api_router)

# Include CSRF token endpoint
app.include_router(csrf_router.router)

# Include Logging endpoints
app.include_router(logging_router.router)

# Initialize audit logging service
try:
    from app.services.audit_service import AuditService
    audit_service = AuditService()
    app.state.audit_service = audit_service
    logger.info("✓ Audit logging service initialized")
except Exception as e:
    logger.warning(f"Could not initialize audit service: {e}")

# Serve uploaded files only in non-production or when explicitly enabled
if (settings.environment.lower() in ("development", "dev", "testing", "test")) or settings.enable_public_uploads:
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

# Static assets for backend-rendered/email templates
backend_static_dir = Path(__file__).resolve().parent / "static"
if backend_static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(backend_static_dir)), name="static")


# Middleware: block unexpected HTML/XML payloads for API endpoints to reduce attack surface
@app.middleware("http")
async def block_html_payloads(request, call_next):
    try:
        if request.method in ("POST", "PUT", "PATCH"):
            ct = request.headers.get("content-type", "").lower()
            if any(x in ct for x in ("text/html", "application/xhtml+xml", "application/xml")):
                return JSONResponse(status_code=400, content={"detail": "Unexpected HTML/XML content type"})
    except Exception:
        # Best-effort: don't let middleware crash the app
        pass
    return await call_next(request)


@app.middleware("http")
async def enforce_csrf_for_mutations(request, call_next):
    """
    Enforce CSRF token on state-changing API operations when configured.
    Se mantiene aditivo: activo por default solo en producción.
    """
    if not settings.enforce_csrf:
        return await call_next(request)

    method = request.method.upper()
    path = request.url.path
    if method not in ("POST", "PUT", "PATCH", "DELETE"):
        return await call_next(request)
    if not path.startswith("/api/v1/"):
        return await call_next(request)

    # Endpoints públicos y/o de bootstrap excluidos.
    csrf_exempt_paths = {
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/auth/forgot-password",
        "/api/v1/auth/reset-password",
        "/api/v1/auth/confirm-email",
        "/api/csrf-token",
    }
    if path in csrf_exempt_paths:
        return await call_next(request)

    # Si va con Bearer explícito, no depende de cookie y no aplica CSRF clásico.
    auth_header = str(request.headers.get("authorization") or "").strip().lower()
    if auth_header.startswith("bearer "):
        return await call_next(request)

    if not validate_csrf_token(request):
        return JSONResponse(status_code=403, content={"detail": "Invalid or missing CSRF token"})

    return await call_next(request)


# Health check endpoint
@app.get("/health")
@app.get("/api/health")
async def health_check():
    """
    Production-grade health check.
    Verifica DB y Redis cuando están disponibles.
    """
    health = {
        "status": "ok",
        "message": "Cirujano de Sintetizadores API is running",
        "environment": settings.environment,
    }
    checks = {}

    # Check database connectivity
    try:
        from app.core.database import SessionLocal
        from sqlalchemy import text as sa_text
        db = SessionLocal()
        try:
            db.execute(sa_text("SELECT 1"))
            checks["database"] = "ok"
        except Exception as e:
            checks["database"] = f"error: {str(e)[:80]}"
            health["status"] = "degraded"
        finally:
            db.close()
    except Exception:
        checks["database"] = "unavailable"
        health["status"] = "degraded"

    # Check Redis connectivity (optional)
    try:
        import redis as redis_lib
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            r = redis_lib.from_url(redis_url, socket_connect_timeout=2)
            r.ping()
            checks["redis"] = "ok"
        else:
            checks["redis"] = "not configured"
    except Exception:
        checks["redis"] = "unavailable"

    health["checks"] = checks
    status_code = 200 if health["status"] == "ok" else 503
    return JSONResponse(content=health, status_code=status_code)


# Root endpoint
@app.get("/")
async def root():
    return {
        "service": "Cirujano de Sintetizadores",
        "version": "1.0.0",
        "environment": settings.environment,
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


# Error handling
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=settings.DEBUG)
