"""
Servicio reutilizable para sincronización automática de instrumentos.
"""

from __future__ import annotations

import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SYNC_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "sync_instruments.py"
_APP_DATA = Path(__file__).resolve().parents[1] / "data"
INSTRUMENTS_JSON_PATH = _APP_DATA / "instruments.json"
SYNC_METADATA_PATH = _APP_DATA / ".sync_metadata.json"


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_instrument_sync(force: bool = False, timeout_seconds: int = 120, trigger: str = "manual") -> Dict[str, Any]:
    """
    Ejecuta scripts/sync_instruments.py y retorna un resumen de resultado.
    """
    cmd = [sys.executable, str(SYNC_SCRIPT_PATH)]
    if force:
        cmd.append("--force")

    payload: Dict[str, Any] = {
        "success": False,
        "trigger": trigger,
        "force": force,
        "command": " ".join(cmd),
    }

    if not SYNC_SCRIPT_PATH.exists():
        payload["error"] = f"Sync script no encontrado: {SYNC_SCRIPT_PATH}"
        return payload

    try:
        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        payload["return_code"] = result.returncode
        payload["stdout"] = result.stdout[-4000:] if result.stdout else ""
        payload["stderr"] = result.stderr[-2000:] if result.stderr else ""
        payload["success"] = result.returncode == 0
    except subprocess.TimeoutExpired:
        payload["error"] = f"Timeout ejecutando sync (>{timeout_seconds}s)"
        return payload
    except Exception as exc:
        payload["error"] = str(exc)
        return payload

    data = _read_json(INSTRUMENTS_JSON_PATH)
    metadata = _read_json(SYNC_METADATA_PATH)
    if data:
        payload["data"] = data
        payload["total_instruments"] = data.get("total_instruments")
        payload["total_bases"] = data.get("total_bases")
        payload["total_variantes"] = data.get("total_variantes")
        payload["total_fotos"] = data.get("total_fotos")
        payload["validacion"] = data.get("validacion", {})
    if metadata:
        payload["last_sync"] = metadata.get("last_sync")
        payload["status"] = metadata.get("status")

    if payload.get("success"):
        logger.info(
            "Instrument sync OK (trigger=%s, force=%s, fotos=%s, bases=%s)",
            trigger,
            force,
            payload.get("total_fotos"),
            payload.get("total_bases"),
        )
    else:
        logger.warning("Instrument sync FAIL (trigger=%s): %s", trigger, payload.get("error") or payload.get("stderr"))

    return payload


def get_instrument_sync_status() -> Dict[str, Any]:
    """Obtiene estado de sincronización sin ejecutar el script."""
    data = _read_json(INSTRUMENTS_JSON_PATH)
    metadata = _read_json(SYNC_METADATA_PATH)
    return {
        "json_exists": INSTRUMENTS_JSON_PATH.exists(),
        "metadata_exists": SYNC_METADATA_PATH.exists(),
        "total_instruments": data.get("total_instruments"),
        "total_bases": data.get("total_bases"),
        "total_variantes": data.get("total_variantes"),
        "total_fotos": data.get("total_fotos"),
        "validacion": data.get("validacion", {}),
        "last_sync": metadata.get("last_sync"),
        "last_count": metadata.get("last_count"),
        "status": metadata.get("status"),
    }


def get_current_instruments_data() -> Dict[str, Any]:
    """Retorna el JSON actual de instrumentos."""
    return _read_json(INSTRUMENTS_JSON_PATH)
