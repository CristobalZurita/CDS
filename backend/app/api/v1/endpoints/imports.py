from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends, status
from typing import Dict
import threading
import sqlite3
import os
import json
from datetime import datetime
import uuid

from app.core.dependencies import get_current_admin

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
DB_PATH = os.path.join(REPO_ROOT, 'backend', 'instance', 'cirujano.sqlite')

router = APIRouter(prefix="/imports", tags=["imports"])


def _ensure_import_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    ddl_path = os.path.join(REPO_ROOT, 'database', 'ddl_cirujano.sql')
    if os.path.exists(ddl_path):
        try:
            cur.executescript(open(ddl_path, 'r', encoding='utf-8').read())
        except Exception:
            pass
    cur.execute("""
        CREATE TABLE IF NOT EXISTS import_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT UNIQUE NOT NULL,
            source_file TEXT,
            started_at TEXT,
            finished_at TEXT,
            status TEXT,
            summary TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            actor TEXT,
            action TEXT,
            object_type TEXT,
            object_id TEXT,
            details TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    return conn


def _get_db_conn():
    return _ensure_import_db()


def _write_audit(actor: str, action: str, details: Dict):
    """Write an audit_logs entry into the import DB (best-effort)."""
    try:
        conn = _get_db_conn()
    except FileNotFoundError:
        return
    cur = conn.cursor()
    cur.execute('INSERT INTO audit_logs (actor, action, object_type, object_id, details, created_at) VALUES (?, ?, ?, ?, ?, ?)', (
        actor, action, 'import_run', None, json.dumps(details, ensure_ascii=False), datetime.utcnow().isoformat() + 'Z'
    ))
    conn.commit()
    conn.close()


def _run_import_sync(user_id: str | None = None, run_id: str | None = None):
    """
    Ejecuta importación aditiva:
    1) Excel → inventario (productos base)
    2) KiCad → comparación referencial
    """
    try:
        from scripts import import_inventory_excel, kicad_catalog_compare

        excel_path = os.getenv("INVENTORY_EXCEL_PATH") or os.path.join(REPO_ROOT, "Inventario_Cirujanosintetizadores.xlsx")
        kicad_path = os.getenv("KICAD_SYMBOLS_PATH") or "/usr/share/kicad/symbols"

        import_inventory_excel.main_from_args(excel_path=excel_path, apply=True)
        kicad_catalog_compare.main_from_args(excel_path=excel_path, kicad_path=kicad_path)

        _write_audit(actor=(user_id or 'system'), action='import.finished', details={'note': 'import completed', 'run_id': run_id})
    except Exception as e:
        _write_audit(actor=(user_id or 'system'), action='import.failed', details={'error': str(e), 'run_id': run_id})
        raise


@router.post('/run', status_code=status.HTTP_200_OK)
def create_import(background_tasks: BackgroundTasks, user: dict = Depends(get_current_admin)) -> Dict:
    """Start an import run asynchronously and return run_id.

    Requires: admin role (via dependency `get_current_admin`).
    """
    # For POC we run import in a background thread so request returns quickly
    # record request immediately for auditability
    try:
        _write_audit(actor=str(user.get('user_id')), action='import.requested', details={'initiated_by': user.get('username')})
    except Exception:
        pass

    # generate a run id so caller can reference it immediately
    run_id = str(uuid.uuid4())
    # Ensure DB/tables exist before inserting queued run
    try:
        conn = _get_db_conn()
        cur = conn.cursor()
        # attempt to ensure tables exist by loading DDL if available
        ddl_path = os.path.join(REPO_ROOT, 'database', 'ddl_cirujano.sql')
        if os.path.exists(ddl_path):
            try:
                cur.executescript(open(ddl_path, 'r', encoding='utf-8').read())
            except Exception:
                # be best-effort
                pass

        cur.execute('INSERT INTO import_runs (run_id, source_file, started_at, status) VALUES (?, ?, ?, ?)', (run_id, os.path.basename(REPO_ROOT), None, 'queued'))
        conn.commit()
    except Exception:
        # best-effort: ignore DB insertion failures here
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass

    th = threading.Thread(target=_run_import_sync, kwargs={'user_id': str(user.get('user_id')), 'run_id': run_id}, daemon=True)
    th.start()
    return {"status": "started", "run_id": run_id}


@router.get('/{run_id}')
def get_import_status(run_id: str, user: dict = Depends(get_current_admin)):
    try:
        conn = _get_db_conn()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='Import DB not initialized')
    cur = conn.cursor()
    cur.execute('SELECT run_id, status, started_at, finished_at, summary FROM import_runs WHERE run_id = ?', (run_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail='Run not found')
    return {
        'run_id': row[0],
        'status': row[1],
        'started_at': row[2],
        'finished_at': row[3],
        'summary': row[4]
    }
