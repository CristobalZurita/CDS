import os
import importlib
import sys
import types


def test_missing_secrets_in_production(tmp_path, monkeypatch):
    # Ensure that when ENVIRONMENT=production and secrets missing, importing config raises ValueError
    monkeypatch.setenv("ENVIRONMENT", "production")
    # Make sure secrets are not set
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.delenv("JWT_SECRET", raising=False)

    # Reload the module to trigger validation
    module_name = "backend.app.core.config"
    if module_name in sys.modules:
        del sys.modules[module_name]
    try:
        importlib.import_module(module_name)
        assert False, "Importing config should have raised ValueError when secrets missing in production"
    except ValueError as e:
        assert "Missing required environment variables for production" in str(e)


def test_no_raise_in_development(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("SECRET_KEY", "dummy")
    monkeypatch.setenv("JWT_SECRET", "dummy")

    # Reload safe
    import importlib, sys
    module_name = "backend.app.core.config"
    if module_name in sys.modules:
        del sys.modules[module_name]
    mod = importlib.import_module(module_name)
    assert hasattr(mod, "get_settings")
    settings = mod.get_settings()
    assert settings.secret_key == "dummy"
    assert settings.jwt_secret == "dummy"
