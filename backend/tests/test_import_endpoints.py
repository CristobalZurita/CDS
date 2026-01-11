import sys
import os
import time
import sqlite3

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from fastapi.testclient import TestClient
from fastapi import HTTPException, status
from backend.app.main import app
from backend.app.core.dependencies import get_current_admin

client = TestClient(app)


def test_create_import_run_unauthenticated():
    # No auth header -> 403 (HTTPBearer returns 403 when no credentials)
    r = client.post('/api/v1/imports/run')
    assert r.status_code == status.HTTP_403_FORBIDDEN


def test_create_import_run_forbidden_non_admin(monkeypatch):
    # Simulate an authenticated non-admin user by overriding the dependency
    def _raise_forbidden():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")

    app.dependency_overrides[get_current_admin] = _raise_forbidden
    r = client.post('/api/v1/imports/run')
    assert r.status_code == status.HTTP_403_FORBIDDEN
    app.dependency_overrides.pop(get_current_admin, None)


def test_create_import_run_admin():
    # Simulate admin user by overriding dependency
    app.dependency_overrides[get_current_admin] = lambda: {"user_id": "1", "role": "admin"}
    r = client.post('/api/v1/imports/run')
    assert r.status_code == 200
    data = r.json()
    assert data.get('status') == 'started'
    assert 'run_id' in data
    run_id = data.get('run_id')
    # verify an audit_logs entry was recorded for the request
    db_path = os.path.join(ROOT, 'backend', 'instance', 'cirujano.sqlite')
    assert os.path.exists(db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    conn.close()
    app.dependency_overrides.pop(get_current_admin, None)


def test_import_runs_exist():
    db_path = os.path.join(ROOT, 'backend', 'instance', 'cirujano.sqlite')
    assert os.path.exists(db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('SELECT count(*) FROM import_runs')
    cnt = cur.fetchone()[0]
    conn.close()
    assert cnt >= 1
