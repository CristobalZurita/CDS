#!/usr/bin/env python3
"""
Script para inicializar base de datos con usuario de prueba
Uso: python backend/scripts/init_db_and_seed.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import asyncio
from app.core.database import init_db, SessionLocal
from app.models.user import User, UserRole
from passlib.context import CryptContext

# Simple bcrypt context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

def hash_pwd(password: str) -> str:
    """Hash password using bcrypt"""
    try:
        return pwd_context.hash(password[:72])  # Bcrypt limit
    except Exception as e:
        # Fallback: Just return the password with a simple prefix for testing
        print(f"⚠️  Bcrypt error: {e}, using plaintext for testing")
        return f"$2b$12$dummy{password[:48]}"



async def main():
    print("🔧 Inicializando base de datos...")
    
    try:
        # Initialize database
        await init_db()
        print("✅ Base de datos inicializada")
    except Exception as e:
        print(f"⚠️  Database initialization warning: {e}")
        print("  (Continuando de todas formas...)")
    
    # Create session
    db = SessionLocal()
    
    try:
        # Check if test user already exists
        existing_user = db.query(User).filter(User.email == "test@example.com").first()
        if existing_user:
            print(f"ℹ️  Usuario test ya existe (ID: {existing_user.id})")
        else:
            # Create test user
            test_user = User(
                email="test@example.com",
                username="testuser",
                full_name="Test User",
                hashed_password=hash_pwd("test12"),  # Shorter password for bcrypt compat
                phone="+56982957538",
                is_active=True,
                role=UserRole.CLIENT
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            print(f"✅ Usuario test creado (ID: {test_user.id})")
            print(f"   Email: test@example.com")
            print(f"   Password: test12")
        
        # Create admin user
        existing_admin = db.query(User).filter(User.email == "admin@example.com").first()
        if existing_admin:
            print(f"ℹ️  Usuario admin ya existe (ID: {existing_admin.id})")
        else:
            admin_user = User(
                email="admin@example.com",
                username="admin",
                full_name="Admin User",
                hashed_password=hash_pwd("admin12"),  # Shorter password for bcrypt compat
                phone="+56982957538",
                is_active=True,
                role=UserRole.ADMIN
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print(f"✅ Usuario admin creado (ID: {admin_user.id})")
            print(f"   Email: admin@example.com")
            print(f"   Password: admin12")
        
        # === SEED PERMISOS Y ROLES (ADITIVO) ===
        print("\n🔐 Inicializando permisos y roles...")
        try:
            from app.services.permission_service import PermissionService
            perm_svc = PermissionService(db)
            perm_svc.init_default_permissions()
            perm_svc.init_default_roles()

            permissions = perm_svc.list_permissions()
            roles = perm_svc.list_roles()
            print(f"   ✅ {len(permissions)} permisos, {len(roles)} roles creados")

            # Asignar rol super_admin al usuario admin si existe
            if existing_admin or 'admin_user' in dir():
                admin = existing_admin or admin_user
                super_admin_role = perm_svc.get_role_by_name("super_admin")
                if super_admin_role:
                    perm_svc.assign_role_to_user(admin.id, super_admin_role.id)
                    print(f"   ✅ Rol super_admin asignado a admin (ID: {admin.id})")
        except Exception as perm_error:
            print(f"   ⚠️  Permisos no inicializados: {perm_error}")

        print("\n✅ Base de datos lista para usar")
        print("\n📝 Para testear login:")
        print("   curl -X POST http://127.0.0.1:8000/api/v1/auth/login \\")
        print("     -H 'Content-Type: application/json' \\")
        print("     -d '{\"email\":\"test@example.com\",\"password\":\"test12\"}'")
        print("\n   O con admin:")
        print("   curl -X POST http://127.0.0.1:8000/api/v1/auth/login \\")
        print("     -H 'Content-Type: application/json' \\")
        print("     -d '{\"email\":\"admin@example.com\",\"password\":\"admin12\"}'")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
