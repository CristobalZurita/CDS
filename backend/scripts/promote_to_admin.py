#!/usr/bin/env python3
"""Promote a user to ADMIN in a controlled, auditable way.

Usage:
  python backend/scripts/promote_to_admin.py --email contacto@... [--yes]

The script:
 - Looks up the user by email
 - Shows the current role and asks for confirmation (unless --yes)
 - Sets role = 'ADMIN' (SQLAlchemy enum name)
 - Creates an audit log entry via create_audit
"""
import argparse
import os
from backend.app.core.database import SessionLocal
from backend.app.models.user import User
from backend.app.services.logging_service import create_audit


def promote(email: str, assume_yes: bool = False) -> None:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"User with email {email} not found")
            return

        print(f"Found user: id={user.id}, username={user.username}, role={user.role}")
        if not assume_yes:
            confirm = input(f"Promote {user.email} to ADMIN? (yes/no): ")
            if confirm.lower() not in ("y", "yes"):
                print("Aborting.")
                return

        user.role = 'ADMIN'  # SQLAlchemy Enum expects name
        db.add(user)
        db.commit()
        db.refresh(user)

        # Audit the promotion
        try:
            create_audit(event_type="user.promote", user_id=user.id, details={"email": user.email, "new_role": "ADMIN"}, message="Promoted user to ADMIN via script")
        except Exception:
            print("Warning: could not persist audit record, check logs.")

        print(f"User {user.email} promoted to ADMIN")
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", required=True, help="Email of the user to promote")
    parser.add_argument("--yes", action="store_true", help="Assume yes and perform promotion non-interactively")
    args = parser.parse_args()

    promote(args.email, assume_yes=args.yes)


if __name__ == "__main__":
    main()
