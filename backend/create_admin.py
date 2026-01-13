#!/usr/bin/env python3
"""
Script para crear usuario administrador inicial
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.models.user import User, UserRole
from backend.app.core.security import hash_password
from backend.app.core.config import settings
from datetime import datetime

def create_admin():
    engine = create_engine(settings.database_url, connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {})
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # Check if admin exists
        existing_admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if existing_admin:
            print(f"✓ Admin user already exists: {existing_admin.email}")
            return

        # Create admin user
        admin = User(
            email="admin@cirujanodesintetizadores.cl",
            username="admin",
            full_name="Administrador",
            hashed_password=hash_password("REDACTED"),
            phone="+56912345678",
            role=UserRole.ADMIN,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print("✓ Admin user created successfully")
        print(f"  Email: {admin.email}")
        print(f"  Username: {admin.username}")
        print(f"  Password: REDACTED")
        print(f"  Role: {admin.role}")
        print("\n⚠️  IMPORTANT: Change the admin password after first login!")

    except Exception as e:
        print(f"✗ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
