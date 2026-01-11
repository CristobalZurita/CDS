import os
import sqlite3
import sys
from pathlib import Path

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def test_import_creates_run():
    # importer is a script; ensure it ran earlier (we invoked it in CI/locally)
    db_path = os.path.join(ROOT, 'backend', 'instance', 'cirujano.sqlite')
    assert os.path.exists(db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('SELECT count(*) FROM import_runs')
    cnt = cur.fetchone()[0]
    assert cnt >= 1
    conn.close()
