#!/usr/bin/env python3
"""Seed stable E2E users into the local SQLite database.

Usage:
  backend/.venv/bin/python scripts/e2e/seed_users.py
"""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT / "backend"
DB_PATH = Path(os.getenv("E2E_DB_PATH", str(BACKEND_DIR / "cirujano.db")))
from passlib.hash import pbkdf2_sha256


def hash_password(password: str) -> str:
    return pbkdf2_sha256.hash(password)


def ensure_legacy_roles(cursor: sqlite3.Cursor) -> None:
    cursor.execute(
        "INSERT OR IGNORE INTO user_roles (id, name, description, permissions) VALUES (1, 'admin', 'Admin', NULL)"
    )
    cursor.execute(
        "INSERT OR IGNORE INTO user_roles (id, name, description, permissions) VALUES (2, 'technician', 'Technician', NULL)"
    )
    cursor.execute(
        "INSERT OR IGNORE INTO user_roles (id, name, description, permissions) VALUES (3, 'client', 'Client', NULL)"
    )


def get_system_role_id(cursor: sqlite3.Cursor, role_name: str) -> int | None:
    row = cursor.execute("SELECT id FROM roles WHERE name = ?", (role_name,)).fetchone()
    return int(row[0]) if row else None


def ensure_client_record(
    cursor: sqlite3.Cursor,
    *,
    user_id: int,
    name: str,
    email: str,
    phone: str,
) -> None:
    existing = cursor.execute(
        "SELECT id FROM clients WHERE user_id = ? LIMIT 1",
        (user_id,),
    ).fetchone()
    now = datetime.utcnow().isoformat()
    if existing:
        cursor.execute(
            """
            UPDATE clients
            SET name = ?, email = ?, phone = ?, updated_at = ?
            WHERE id = ?
            """,
            (name, email, phone, now, int(existing[0])),
        )
        return

    cursor.execute(
        """
        INSERT INTO clients (
            user_id, name, email, phone, total_repairs, total_spent, created_at, updated_at
        ) VALUES (?, ?, ?, ?, 0, 0, ?, ?)
        """,
        (user_id, name, email, phone, now, now),
    )


def ensure_user(
    cursor: sqlite3.Cursor,
    *,
    email: str,
    username: str,
    password: str,
    first_name: str,
    last_name: str,
    role_id: int,
    phone: str,
    assigned_role_name: str | None = None,
) -> None:
    now = datetime.utcnow().isoformat()
    hashed_password = hash_password(password)
    existing = cursor.execute(
        "SELECT id FROM users WHERE email = ? LIMIT 1",
        (email,),
    ).fetchone()

    if existing:
        user_id = int(existing[0])
        cursor.execute(
            """
            UPDATE users
            SET username = ?, hashed_password = ?, first_name = ?, last_name = ?,
                phone = ?, role_id = ?, is_active = 1, is_verified = 1,
                two_factor_enabled = 0, updated_at = ?
            WHERE id = ?
            """,
            (
                username,
                hashed_password,
                first_name,
                last_name,
                phone,
                role_id,
                now,
                user_id,
            ),
        )
    else:
        cursor.execute(
            """
            INSERT INTO users (
                email, username, hashed_password, first_name, last_name, phone,
                role_id, is_active, is_verified, created_at, updated_at,
                two_factor_enabled, two_factor_method
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, 1, ?, ?, 0, 'email')
            """,
            (
                email,
                username,
                hashed_password,
                first_name,
                last_name,
                phone,
                role_id,
                now,
                now,
            ),
        )
        user_id = int(cursor.lastrowid)

    full_name = f"{first_name} {last_name}".strip()
    if role_id == 3:
        ensure_client_record(
            cursor,
            user_id=user_id,
            name=full_name,
            email=email,
            phone=phone,
        )

    if assigned_role_name:
        system_role_id = get_system_role_id(cursor, assigned_role_name)
        if system_role_id is not None:
            cursor.execute(
                """
                INSERT OR IGNORE INTO user_role_assignments (user_id, role_id, created_at)
                VALUES (?, ?, ?)
                """,
                (user_id, system_role_id, now),
            )


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        ensure_legacy_roles(cursor)

        ensure_user(
            cursor,
            email="e2e.admin@example.com",
            username="e2e_admin",
            password=os.getenv("E2E_ADMIN_PASSWORD", "admin12"),
            first_name="E2E",
            last_name="Admin",
            role_id=1,
            phone="+56911111111",
            assigned_role_name="super_admin",
        )
        ensure_user(
            cursor,
            email="e2e.client@example.com",
            username="e2e_client",
            password=os.getenv("E2E_CLIENT_PASSWORD", "client12"),
            first_name="E2E",
            last_name="Client",
            role_id=3,
            phone="+56922222222",
        )

        conn.commit()
        print(f"Seeded E2E users in {DB_PATH}")
        print("Admin:  e2e.admin@example.com / admin12")
        print("Client: e2e.client@example.com / client12")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
