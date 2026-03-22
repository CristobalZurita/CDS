"""
Configuration settings for Cirujano de Sintetizadores API
"""

from pydantic import BaseModel, ConfigDict
from functools import lru_cache
from typing import Optional
import os
from dotenv import load_dotenv

from app.core.business_config import business_config


def _load_dotenv_for_env() -> None:
    """Load a .env file from backend/.env (preferred) or repo root .env."""
    if os.getenv("ENVIRONMENT", "development").lower() in ("production", "prod"):
        return

    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    repo_root = os.path.abspath(os.path.join(backend_dir, ".."))
    backend_env = os.path.join(backend_dir, ".env")
    root_env = os.path.join(repo_root, ".env")

    if os.path.exists(backend_env):
        load_dotenv(backend_env)
    elif os.path.exists(root_env):
        load_dotenv(root_env)


_load_dotenv_for_env()

_ENVIRONMENT_NAME = os.getenv("ENVIRONMENT", "development").lower()
_IS_TEST_ENV = _ENVIRONMENT_NAME in ("test", "testing")
_IS_PROD_ENV = _ENVIRONMENT_NAME in ("production", "prod")


class Settings(BaseModel):
    """Application settings"""
    model_config = ConfigDict(case_sensitive=False)

    # API Configuration
    api_title: str = business_config.api_title
    api_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    environment: str = os.getenv("ENVIRONMENT", "development")

    # Database Configuration
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./cirujano.db")
    database_echo: bool = False

    # JWT Configuration - do NOT include production secrets in code
    secret_key: Optional[str] = os.getenv("SECRET_KEY")
    jwt_secret: Optional[str] = os.getenv("JWT_SECRET")
    jwt_refresh_secret: Optional[str] = os.getenv("JWT_REFRESH_SECRET")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    allow_token_in_response: bool = os.getenv("ALLOW_TOKEN_IN_RESPONSE", "false").lower() == "true"
    enable_api_docs: bool = os.getenv("ENABLE_API_DOCS", "false").lower() == "true"
    enable_public_uploads: bool = os.getenv("ENABLE_PUBLIC_UPLOADS", "false").lower() == "true"
    enable_instrument_auto_sync: bool = os.getenv(
        "ENABLE_INSTRUMENT_AUTO_SYNC",
        "false" if _IS_TEST_ENV else "true",
    ).lower() == "true"
    instrument_sync_on_startup: bool = os.getenv(
        "INSTRUMENT_SYNC_ON_STARTUP",
        "false" if _IS_TEST_ENV else "true",
    ).lower() == "true"
    instrument_sync_interval_minutes: int = int(os.getenv("INSTRUMENT_SYNC_INTERVAL_MINUTES", "360"))
    enforce_csrf: bool = os.getenv(
        "ENFORCE_CSRF",
        "true" if _IS_PROD_ENV else "false",
    ).lower() == "true"

    # CORS Configuration
    # ALLOWED_ORIGINS or CORS_ORIGINS can be provided as a comma-separated env var
    _allowed_origins_env: Optional[str] = os.getenv("ALLOWED_ORIGINS") or os.getenv("CORS_ORIGINS")
    if _allowed_origins_env:
        allowed_origins: list = [o.strip() for o in _allowed_origins_env.split(",") if o.strip()]
    else:
        # sensible defaults for development
        allowed_origins: list = [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:5174",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5174",
        ]

    # Email Configuration
    smtp_server: Optional[str] = os.getenv("SMTP_HOST") or os.getenv("SMTP_SERVER")
    smtp_port: Optional[int] = int(os.getenv("SMTP_PORT")) if os.getenv("SMTP_PORT") else None
    smtp_user: Optional[str] = os.getenv("SMTP_USER")
    smtp_password: Optional[str] = os.getenv("SMTP_PASSWORD")
    from_email: Optional[str] = os.getenv("FROM_EMAIL") or os.getenv("SMTP_FROM_EMAIL")
    smtp_use_tls: bool = os.getenv("SMTP_USE_TLS", "false").lower() == "true"
    smtp_use_ssl: bool = os.getenv("SMTP_USE_SSL", "true").lower() == "true"

    public_base_url: str = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000")
    whatsapp_token: Optional[str] = os.getenv("WHATSAPP_TOKEN")
    whatsapp_phone_id: Optional[str] = os.getenv("WHATSAPP_PHONE_ID")
    whatsapp_api_url: str = os.getenv("WHATSAPP_API_URL", "https://graph.facebook.com/v17.0")
    whatsapp_template_name: Optional[str] = os.getenv("WHATSAPP_TEMPLATE_NAME")
    whatsapp_template_lang: str = os.getenv("WHATSAPP_TEMPLATE_LANG", "en_US")
    whatsapp_webhook_verify_token: Optional[str] = os.getenv("WHATSAPP_WEBHOOK_VERIFY_TOKEN")

    # Payment Gateway Configuration
    # Set PAYMENT_GATEWAY to "transbank" or "mercadopago"
    payment_gateway: str = os.getenv("PAYMENT_GATEWAY", "")
    # Transbank Webpay Plus
    transbank_commerce_code: Optional[str] = os.getenv("TRANSBANK_COMMERCE_CODE")
    transbank_api_key: Optional[str] = os.getenv("TRANSBANK_API_KEY")
    transbank_environment: str = os.getenv("TRANSBANK_ENVIRONMENT", "integration")  # "integration" | "production"
    # MercadoPago
    mercadopago_access_token: Optional[str] = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
    mercadopago_webhook_secret: Optional[str] = os.getenv("MERCADOPAGO_WEBHOOK_SECRET")

    # Pricing Configuration
    diagnostic_fee: int = 0  # Free diagnostic
    service_multipliers: dict = {
        "legendary": 1.8,
        "professional": 1.5,
        "standard": 1.2,
        "specialized": 1.3,
        "boutique": 1.4,
        "historic": 1.3,
    }

    value_multipliers: dict = {
        "low": 1.0,  # < 500000 CLP
        "medium": 1.3,  # 500000 - 2000000 CLP
        "high": 1.6,  # 2000000 - 5000000 CLP
        "premium": 2.0,  # > 5000000 CLP
    }

    # ── Chat inteligente — cascada multi-proveedor ──────────────────────────
    # Gemini (Google)
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite")
    # Groq (free tier: llama, gemma, mixtral)
    groq_api_key: Optional[str] = os.getenv("GROQ_API_KEY")
    # Mistral AI (free tier: mistral-small, open-mistral-7b)
    mistral_api_key: Optional[str] = os.getenv("MISTRAL_API_KEY")
    chat_max_turns: int = int(os.getenv("CHAT_MAX_TURNS", "20"))
    # Cascada: formato "proveedor:modelo" — se intenta en orden.
    # Las entradas sin API key configurada se saltan automáticamente.
    chat_model_cascade: list = [
        m.strip() for m in os.getenv(
            "CHAT_MODEL_CASCADE",
            "gemini:gemini-2.0-flash-lite,"
            "groq:llama-3.1-8b-instant,"
            "groq:llama-3.3-70b-versatile,"
            "mistral:mistral-small-latest,"
            "gemini:gemini-2.0-flash,"
            "gemini:gemini-2.5-flash"
        ).split(",") if m.strip()
    ]

    # ── Google Calendar Configuration ──────────────────────────
    google_calendar_credentials_file: Optional[str] = os.getenv("GOOGLE_CALENDAR_CREDENTIALS_FILE")
    google_calendar_id: str = os.getenv("GOOGLE_CALENDAR_ID", "primary")


# Instantiate settings with environment variables
settings = Settings()

# Validate critical secrets in production-like environments
if settings.environment and settings.environment.lower() in ("production", "prod"):
    missing = []
    if not settings.secret_key:
        missing.append("SECRET_KEY")
    if not settings.jwt_secret:
        missing.append("JWT_SECRET")
    if not settings.jwt_refresh_secret:
        missing.append("JWT_REFRESH_SECRET")
    if missing:
        raise ValueError(f"Missing required environment variables for production: {', '.join(missing)}")
    if settings.jwt_refresh_secret == settings.jwt_secret:
        raise ValueError("JWT_REFRESH_SECRET must be different from JWT_SECRET in production")
    if len(settings.jwt_refresh_secret) < 64 or len(settings.jwt_secret) < 64:
        raise ValueError("JWT secrets must be at least 64 characters in production")


def get_settings() -> Settings:
    """Get settings instance"""
    return settings
