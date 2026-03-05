import importlib
import os
import sys

import pytest


def _reload_config(env: dict) -> None:
    original = os.environ.copy()
    os.environ.clear()
    os.environ.update(env)
    try:
        if "app.core.config" in sys.modules:
            del sys.modules["app.core.config"]
        importlib.import_module("app.core.config")
    finally:
        os.environ.clear()
        os.environ.update(original)


def test_refresh_secret_required_in_production():
    env = {
        "ENVIRONMENT": "production",
        "SECRET_KEY": "a" * 64,
        "JWT_SECRET": "b" * 64,
    }
    with pytest.raises(ValueError):
        _reload_config(env)


def test_refresh_secret_must_differ_in_production():
    env = {
        "ENVIRONMENT": "production",
        "SECRET_KEY": "a" * 64,
        "JWT_SECRET": "b" * 64,
        "JWT_REFRESH_SECRET": "b" * 64,
    }
    with pytest.raises(ValueError):
        _reload_config(env)
