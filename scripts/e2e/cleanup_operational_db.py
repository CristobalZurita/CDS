#!/usr/bin/env python3
"""Remove E2E fixtures and orphaned repair artifacts from the operative SQLite DB.

Usage:
  backend/.venv/bin/python scripts/e2e/cleanup_operational_db.py --apply
"""

from __future__ import annotations

import argparse
import os
import shutil
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT / "backend"
DEFAULT_DB_PATH = BACKEND_DIR / "cirujano.db"
DEFAULT_UPLOADS_DIR = BACKEND_DIR / "uploads"

USER_EMAIL_PATTERNS = (
    "e2e.%@example.com",
    "route-timeout@example.com",
)
USER_USERNAME_PATTERNS = (
    "e2e_%",
    "rtimeout",
)
CLIENT_NAME_PATTERNS = (
    "E2E %",
    "rtimeout",
)
DEVICE_MODEL_PATTERNS = (
    "%E2E%",
    "Route E2E %",
    "Sintetizador E2E %",
    "Repair E2E %",
    "CRUD Repair %",
)
REPAIR_PROBLEM_PATTERNS = (
    "%E2E%",
    "%prueba E2E%",
)


@dataclass
class CleanupTarget:
    user_ids: set[int]
    client_ids: set[int]
    device_ids: set[int]
    repair_ids: set[int]
    orphan_repair_ids: set[int]
    photo_paths: set[str]
    signature_paths: set[str]


def _ids_from_query(conn: sqlite3.Connection, query: str, params: tuple = ()) -> set[int]:
    return {int(row[0]) for row in conn.execute(query, params).fetchall() if row and row[0] is not None}


def _collect_targets(conn: sqlite3.Connection) -> CleanupTarget:
    user_ids: set[int] = set()
    for pattern in USER_EMAIL_PATTERNS:
        user_ids |= _ids_from_query(conn, "SELECT id FROM users WHERE email LIKE ?", (pattern,))
    for pattern in USER_USERNAME_PATTERNS:
        user_ids |= _ids_from_query(conn, "SELECT id FROM users WHERE username LIKE ?", (pattern,))

    client_ids: set[int] = set()
    client_ids |= _ids_from_query(conn, "SELECT id FROM clients WHERE user_id IN ({})".format(",".join("?" * len(user_ids))), tuple(user_ids)) if user_ids else set()
    for pattern in USER_EMAIL_PATTERNS:
        client_ids |= _ids_from_query(conn, "SELECT id FROM clients WHERE email LIKE ?", (pattern,))
    for pattern in CLIENT_NAME_PATTERNS:
        client_ids |= _ids_from_query(conn, "SELECT id FROM clients WHERE name LIKE ?", (pattern,))

    device_ids: set[int] = set()
    device_ids |= _ids_from_query(conn, "SELECT id FROM devices WHERE client_id IN ({})".format(",".join("?" * len(client_ids))), tuple(client_ids)) if client_ids else set()
    for pattern in DEVICE_MODEL_PATTERNS:
        device_ids |= _ids_from_query(conn, "SELECT id FROM devices WHERE model LIKE ?", (pattern,))

    repair_ids: set[int] = set()
    repair_ids |= _ids_from_query(conn, "SELECT id FROM repairs WHERE device_id IN ({})".format(",".join("?" * len(device_ids))), tuple(device_ids)) if device_ids else set()
    for pattern in REPAIR_PROBLEM_PATTERNS:
        repair_ids |= _ids_from_query(conn, "SELECT id FROM repairs WHERE problem_reported LIKE ?", (pattern,))

    existing_repairs = _ids_from_query(conn, "SELECT id FROM repairs")
    orphan_repair_ids: set[int] = set()
    for table in ("repair_photos", "photo_upload_requests", "signature_requests"):
        orphan_repair_ids |= {
            int(row[0])
            for row in conn.execute(f"SELECT DISTINCT repair_id FROM {table} WHERE repair_id IS NOT NULL").fetchall()
            if row[0] is not None and int(row[0]) not in existing_repairs
        }

    photo_paths = {
        str(row[0])
        for row in conn.execute(
            """
            SELECT photo_url
            FROM repair_photos
            WHERE repair_id IN ({})
               OR repair_id IN ({})
            """.format(
                ",".join("?" * len(repair_ids)) if repair_ids else "NULL",
                ",".join("?" * len(orphan_repair_ids)) if orphan_repair_ids else "NULL",
            ),
            tuple(repair_ids) + tuple(orphan_repair_ids),
        ).fetchall()
        if row[0]
    }

    signature_paths = {
        str(path_value)
        for row in conn.execute(
            """
            SELECT signature_ingreso_path, signature_retiro_path
            FROM repairs
            WHERE id IN ({})
            """.format(",".join("?" * len(repair_ids)) if repair_ids else "NULL"),
            tuple(repair_ids),
        ).fetchall()
        for path_value in row
        if path_value
    }

    return CleanupTarget(
        user_ids=user_ids,
        client_ids=client_ids,
        device_ids=device_ids,
        repair_ids=repair_ids,
        orphan_repair_ids=orphan_repair_ids,
        photo_paths=photo_paths,
        signature_paths=signature_paths,
    )


def _delete_by_ids(conn: sqlite3.Connection, table: str, column: str, ids: set[int]) -> None:
    if not ids:
        return
    placeholders = ",".join("?" * len(ids))
    conn.execute(f"DELETE FROM {table} WHERE {column} IN ({placeholders})", tuple(ids))


def _remove_path(base_dir: Path, stored_path: str) -> None:
    relative = stored_path.strip().lstrip("/")
    candidates = [
        ROOT / relative,
        BACKEND_DIR / relative,
        base_dir / relative,
    ]
    for candidate in candidates:
        if candidate.exists():
            candidate.unlink(missing_ok=True)
            break


def _remove_repair_dirs(base_dir: Path, repair_ids: set[int]) -> None:
    for repair_id in sorted(repair_ids):
        for relative_dir in (base_dir / "repairs" / f"repair-{repair_id}", base_dir / "signatures" / f"repair-{repair_id}"):
            if relative_dir.exists():
                shutil.rmtree(relative_dir, ignore_errors=True)


def _collect_orphan_upload_repair_ids(base_dir: Path, existing_repair_ids: set[int]) -> set[int]:
    orphan_ids: set[int] = set()
    for section in ("repairs", "signatures"):
        root = base_dir / section
        if not root.exists():
            continue
        for child in root.iterdir():
            if not child.is_dir() or not child.name.startswith("repair-"):
                continue
            try:
                repair_id = int(child.name.split("repair-", 1)[1])
            except ValueError:
                continue
            if repair_id not in existing_repair_ids:
                orphan_ids.add(repair_id)
    return orphan_ids


def _create_backup(db_path: Path) -> Path:
    backup_dir = Path("/tmp")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"{db_path.stem}.pre_e2e_cleanup_{timestamp}{db_path.suffix}"
    shutil.copy2(db_path, backup_path)
    return backup_path


def _apply_cleanup(conn: sqlite3.Connection, target: CleanupTarget) -> None:
    repair_ids = target.repair_ids | target.orphan_repair_ids

    conn.execute("PRAGMA foreign_keys = OFF")

    for table in (
        "diagnostics",
        "stock_movements",
        "payments",
        "repair_component_usage",
        "repair_photos",
        "repair_notes",
        "signature_requests",
        "tickets",
        "photo_upload_requests",
        "invoices",
        "warranties",
        "warranty_claims",
        "repair_intake_sheets",
        "purchase_requests",
    ):
        if table == "warranty_claims":
            _delete_by_ids(conn, table, "new_repair_id", repair_ids)
        else:
            _delete_by_ids(conn, table, "repair_id", repair_ids)

    for table in (
        "quotes",
        "tickets",
        "purchase_requests",
        "invoices",
        "warranties",
        "repair_intake_sheets",
        "appointments",
    ):
        _delete_by_ids(conn, table, "client_id", target.client_ids)

    for table in ("quotes", "repair_intake_sheets"):
        _delete_by_ids(conn, table, "device_id", target.device_ids)

    for table, column in (
        ("clients", "user_id"),
        ("quotes", "created_by"),
        ("repairs", "assigned_to"),
        ("stock_movements", "performed_by"),
        ("payments", "user_id"),
        ("repair_notes", "user_id"),
        ("tickets", "created_by"),
        ("purchase_requests", "created_by"),
        ("two_factor_codes", "user_id"),
        ("ticket_messages", "author_id"),
        ("user_role_assignments", "user_id"),
        ("repair_intake_sheets", "created_by"),
        ("invoices", "created_by"),
        ("invoices", "voided_by"),
        ("warranties", "created_by"),
        ("warranties", "voided_by"),
        ("warranty_claims", "submitted_by"),
        ("warranty_claims", "evaluated_by"),
    ):
        _delete_by_ids(conn, table, column, target.user_ids)

    _delete_by_ids(conn, "repairs", "id", target.repair_ids)
    _delete_by_ids(conn, "devices", "id", target.device_ids)
    _delete_by_ids(conn, "clients", "id", target.client_ids)
    _delete_by_ids(conn, "users", "id", target.user_ids)

    # Remove broken rows that reference non-existent repairs after cleanup.
    conn.execute("DELETE FROM repair_photos WHERE repair_id IS NOT NULL AND repair_id NOT IN (SELECT id FROM repairs)")
    conn.execute("DELETE FROM photo_upload_requests WHERE repair_id IS NOT NULL AND repair_id NOT IN (SELECT id FROM repairs)")
    conn.execute("DELETE FROM signature_requests WHERE repair_id IS NOT NULL AND repair_id NOT IN (SELECT id FROM repairs)")

    conn.commit()


def _print_summary(target: CleanupTarget) -> None:
    print("Usuarios E2E:", sorted(target.user_ids))
    print("Clientes E2E:", sorted(target.client_ids))
    print("Devices E2E:", sorted(target.device_ids))
    print("Repairs E2E:", sorted(target.repair_ids))
    print("Repairs huérfanas ligadas a artefactos:", sorted(target.orphan_repair_ids))
    print("Fotos a remover:", len(target.photo_paths))
    print("Firmas a remover:", len(target.signature_paths))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db-path", default=str(DEFAULT_DB_PATH))
    parser.add_argument("--uploads-dir", default=str(DEFAULT_UPLOADS_DIR))
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    db_path = Path(args.db_path).resolve()
    uploads_dir = Path(args.uploads_dir).resolve()

    conn = sqlite3.connect(db_path)
    try:
        target = _collect_targets(conn)
        _print_summary(target)

        if not args.apply:
            print("Dry-run solamente. Usa --apply para ejecutar la limpieza.")
            return

        backup_path = _create_backup(db_path)
        print(f"Backup creado en: {backup_path}")

        _apply_cleanup(conn, target)
        existing_repair_ids = _ids_from_query(conn, "SELECT id FROM repairs")
    finally:
        conn.close()

    for photo_path in sorted(target.photo_paths):
        _remove_path(uploads_dir, photo_path)
    for signature_path in sorted(target.signature_paths):
        _remove_path(uploads_dir, signature_path)
    orphan_upload_repair_ids = _collect_orphan_upload_repair_ids(uploads_dir, existing_repair_ids)
    _remove_repair_dirs(uploads_dir, target.repair_ids | target.orphan_repair_ids | orphan_upload_repair_ids)

    print("Limpieza E2E aplicada.")


if __name__ == "__main__":
    main()
