#!/usr/bin/env python3
"""Import normalized items into a SQLite database (idempotent).

Writes into `backend/instance/cirujano.sqlite` and records an import_run entry.
"""
from __future__ import annotations
import os
import json
import sqlite3
import uuid
from datetime import datetime

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
NORMALIZED = os.path.join(REPO_ROOT, 'reports', 'normalized_items.json')
DB_PATH = os.path.join(REPO_ROOT, 'backend', 'instance', 'cirujano.sqlite')


def ensure_db(path=DB_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    return conn


def run_import(user_id: str | None = None, run_id: str | None = None):
    if not os.path.exists(NORMALIZED):
        raise SystemExit('Run normalize_excel.py first to produce normalized_items.json')
    with open(NORMALIZED, 'r', encoding='utf-8') as fh:
        items = json.load(fh)

    conn = ensure_db()
    cur = conn.cursor()

    # create tables if not exist (simple DDL that mirrors database/ddl_cirujano.sql)
    cur.executescript(open(os.path.join(REPO_ROOT, 'database', 'ddl_cirujano.sql'), 'r', encoding='utf-8').read())

    provided_run_id = run_id is not None
    if not provided_run_id:
        run_id = str(uuid.uuid4())

    started = datetime.utcnow().isoformat() + 'Z'
    # If the caller already queued a run_id, update that row to running, otherwise insert a new run
    if provided_run_id:
        cur.execute('SELECT run_id FROM import_runs WHERE run_id = ?', (run_id,))
        if cur.fetchone():
            cur.execute('UPDATE import_runs SET started_at = ?, status = ? WHERE run_id = ?', (started, 'running', run_id))
        else:
            cur.execute('INSERT INTO import_runs (run_id, source_file, started_at, status) VALUES (?, ?, ?, ?)', (run_id, os.path.basename(NORMALIZED), started, 'running'))
    else:
        cur.execute('INSERT INTO import_runs (run_id, source_file, started_at, status) VALUES (?, ?, ?, ?)', (run_id, os.path.basename(NORMALIZED), started, 'running'))
    conn.commit()

    # Write an audit_log entry if the table exists
    try:
        cur.execute('INSERT INTO audit_logs (actor, action, object_type, object_id, details, created_at) VALUES (?, ?, ?, ?, ?, ?)', (
            user_id or 'system', 'import.started', 'import_run', None, json.dumps({'run_id': run_id, 'source_file': os.path.basename(NORMALIZED)}), datetime.utcnow().isoformat() + 'Z'
        ))
        conn.commit()
    except Exception:
        # If audit_logs doesn't exist or insert fails, continue silently
        pass

    inserted = 0
    updated = 0
    for it in items:
        sku = it.get('sku')
        name = it.get('name')
        category = it.get('category')

        # find or create category
        cur.execute('SELECT id FROM categories WHERE name = ?', (category,))
        row = cur.fetchone()
        if row:
            cat_id = row[0]
        else:
            cur.execute('INSERT INTO categories (name) VALUES (?)', (category,))
            cat_id = cur.lastrowid

        # upsert item by sku
        cur.execute('SELECT id FROM items WHERE sku = ?', (sku,))
        r = cur.fetchone()
        if r:
            cur.execute('UPDATE items SET name = ?, category_id = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (name, cat_id, r[0]))
            updated += 1
        else:
            cur.execute('INSERT INTO items (sku, name, category_id, stock) VALUES (?, ?, ?, ?)', (sku, name, cat_id, 0))
            inserted += 1

    finished = datetime.utcnow().isoformat() + 'Z'
    summary = f'inserted={inserted},updated={updated}'
    cur.execute('UPDATE import_runs SET finished_at = ?, status = ?, summary = ? WHERE run_id = ?', (finished, 'finished', summary, run_id))
    conn.commit()
    # record finish in audit_logs
    try:
        cur.execute('INSERT INTO audit_logs (actor, action, object_type, object_id, details, created_at) VALUES (?, ?, ?, ?, ?, ?)', (
            user_id or 'system', 'import.finished', 'import_run', None, json.dumps({'run_id': run_id, 'summary': summary}), datetime.utcnow().isoformat() + 'Z'
        ))
        conn.commit()
    except Exception:
        pass
    conn.close()
    print(f'Import finished: {summary} (run_id={run_id})')
    return {'run_id': run_id, 'inserted': inserted, 'updated': updated}


if __name__ == '__main__':
    run_import()
