#!/usr/bin/env python3
"""
Script para inicializar roles base y usuarios de prueba.
ADITIVO: Nuevo script, no modifica archivos existentes.

Uso:
    cd backend
    python scripts/seed_admin.py
"""

import sys
import os
import secrets
import getpass
from pathlib import Path

# Add backend root to path
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root))

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User, UserRole


ROLES = (
    {"id": 1, "name": "admin"},
    {"id": 2, "name": "technician"},
    {"id": 3, "name": "client"},
)

USERS = (
    {
        "email": "admin@test.com",
        "username": "admin",
        "password_env": "SEED_ADMIN_PASSWORD",
        "password_label": "admin user",
        "role": "admin",
        "is_active": 1,
        "is_verified": 1,
        "two_factor_enabled": 0,
    },
    {
        "email": "cliente@test.com",
        "username": "cliente",
        "password_env": "SEED_TEST_PASSWORD",
        "password_label": "client user",
        "role": "client",
        "is_active": 1,
        "is_verified": 1,
        "two_factor_enabled": 0,
    },
)


def _env_name() -> str:
    return os.getenv("ENVIRONMENT", "development").lower()


def _resolve_seed_password(label: str, env_var: str) -> str:
    env_value = os.getenv(env_var)
    if env_value:
        return env_value

    env_name = _env_name()
    if env_name in ("production", "prod"):
        if sys.stdin.isatty():
            return getpass.getpass(f"{label} (env {env_var}): ")
        raise RuntimeError(f"Missing {env_var} for production seed")

    generated = secrets.token_urlsafe(16)
    print(f"⚠️  {env_var} no definido; se genera password temporal para {label}: {generated}")
    return generated


def ensure_roles(db) -> None:
    print("👥 Verificando roles base...")
    for role_data in ROLES:
        existing = db.query(UserRole).filter(UserRole.name == role_data["name"]).first()
        if existing:
            print(f"   ✓ Role existente: {existing.id} | {existing.name}")
            continue

        role = UserRole(
            id=role_data["id"],
            name=role_data["name"],
        )
        db.add(role)
        db.flush()
        print(f"   + Role creado: {role.id} | {role.name}")


def resolve_username(db, email: str, username: str | None) -> str | None:
    if not username:
        return None

    existing = db.query(User).filter(User.username == username).first()
    if existing and existing.email != email:
        print(f"   ! Username ocupado por otro usuario: {username} -> se crea sin username")
        return None

    return username


def ensure_users(db) -> list[User]:
    print("👤 Verificando usuarios de prueba...")
    resolved_users: list[User] = []
    resolved_passwords = {
        user_data["email"]: _resolve_seed_password(
            user_data["password_label"],
            user_data["password_env"],
        )
        for user_data in USERS
    }

    for user_data in USERS:
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        if existing:
            resolved_users.append(existing)
            print(f"   ✓ Usuario existente: {existing.email}")
            continue

        user = User(
            email=user_data["email"],
            username=resolve_username(db, user_data["email"], user_data["username"]),
            hashed_password=hash_password(resolved_passwords[user_data["email"]]),
            role=user_data["role"],
            is_active=user_data["is_active"],
            is_verified=user_data["is_verified"],
            two_factor_enabled=user_data["two_factor_enabled"],
        )
        db.add(user)
        db.flush()
        resolved_users.append(user)
        print(f"   + Usuario creado: {user.email}")

    return resolved_users


def main():
    print("🔐 Inicializando seed admin...")
    db = SessionLocal()

    try:
        ensure_roles(db)
        users = ensure_users(db)
        db.commit()

        print("\n📋 Resultado:")
        for user in users:
            db.refresh(user)
            print(f"   id={user.id} | email={user.email} | role={user.role}")

        print("\n✅ Seed completado correctamente")
    except Exception as exc:
        db.rollback()
        print(f"❌ Error: {exc}")
        import traceback
        traceback.print_exc()
        raise SystemExit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
