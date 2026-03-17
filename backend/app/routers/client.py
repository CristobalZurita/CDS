"""
Compatibilidad para imports legacy del portal cliente.

La API real monta `app.routers.client_portal`. Este módulo se conserva para
imports históricos en tests o utilidades internas, sin duplicar la
implementación.
"""

from app.routers.client_portal import *  # noqa: F401,F403
