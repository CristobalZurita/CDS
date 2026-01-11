"""
Configuration settings for Cirujano de Sintetizadores API
"""

from pydantic import BaseModel
from functools import lru_cache
from typing import Optional
import os
from dotenv import load_dotenv

# Load .env file only for non-production environments (tests and production should not rely on .env)
if os.getenv("ENVIRONMENT", "development").lower() not in ("production", "prod"):
    load_dotenv()


class Settings(BaseModel):
    """Application settings"""

    # API Configuration
    api_title: str = "Cirujano de Sintetizadores API"
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

    # CORS Configuration
    # ALLOWED_ORIGINS can be provided as a comma-separated env var
    _allowed_origins_env: Optional[str] = os.getenv("ALLOWED_ORIGINS")
    if _allowed_origins_env:
        allowed_origins: list = [o.strip() for o in _allowed_origins_env.split(",") if o.strip()]
    else:
        # sensible defaults for development
        allowed_origins: list = [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
        ]

    # Email Configuration
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    from_email: Optional[str] = None

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
    class Config:
        case_sensitive = False


# Instantiate settings with environment variables
settings = Settings()

# Validate critical secrets in production-like environments
if settings.environment and settings.environment.lower() in ("production", "prod"):
    missing = []
    if not settings.secret_key:
        missing.append("SECRET_KEY")
    if not settings.jwt_secret:
        missing.append("JWT_SECRET")
    if missing:
        raise ValueError(f"Missing required environment variables for production: {', '.join(missing)}")


def get_settings() -> Settings:
    """Get settings instance"""
    return settings
