"""
Cirujano de Sintetizadores - Backend API
Sistema integral de gestión para taller de reparación de sintetizadores

FastAPI application with async database support, JWT authentication,
and comprehensive diagnostic/quotation system.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.core.security import verify_crypto_dependencies
from app.core.database import init_db, close_db
from app.api.v1.router import api_router
from app.core.ratelimit import limiter
from slowapi.errors import RateLimitExceeded
from app.routers import csrf as csrf_router
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
    try:
        await close_db()
        logger.info("✓ Database connection closed")
    except Exception as e:
        logger.error(f"✗ Error during shutdown: {e}")


# Initialize FastAPI app
app = FastAPI(
    title="Cirujano de Sintetizadores API",
    description="Sistema integral de gestión para taller de reparación de sintetizadores",
    version="1.0.0",
    lifespan=lifespan,
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


    # Attach rate limiter to the application state and register handler
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


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


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Cirujano de Sintetizadores API is running"}


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
