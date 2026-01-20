#!/usr/bin/env python3
"""
Script para inicializar permisos y roles predefinidos.
ADITIVO: Nuevo script, no modifica existentes.

Uso: python backend/scripts/seed_permissions.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import SessionLocal
from app.services.permission_service import PermissionService


def main():
    print("🔐 Inicializando permisos y roles...")
    
    db = SessionLocal()
    
    try:
        svc = PermissionService(db)
        
        # Inicializar permisos predefinidos
        print("📝 Creando permisos predefinidos...")
        svc.init_default_permissions()
        
        # Contar permisos creados
        permissions = svc.list_permissions()
        print(f"   ✅ {len(permissions)} permisos activos")
        
        # Inicializar roles predefinidos
        print("👥 Creando roles predefinidos...")
        svc.init_default_roles()
        
        # Contar roles creados
        roles = svc.list_roles()
        print(f"   ✅ {len(roles)} roles activos")
        
        # Mostrar resumen
        print("\n📋 Resumen de permisos por recurso:")
        resources = {}
        for perm in permissions:
            if perm.resource not in resources:
                resources[perm.resource] = []
            resources[perm.resource].append(perm.action)
        
        for resource, actions in sorted(resources.items()):
            print(f"   {resource}: {', '.join(actions)}")
        
        print("\n👤 Roles creados:")
        for role in roles:
            perm_count = len(role.permissions)
            print(f"   {role.name} ({role.display_name}): {perm_count} permisos")
        
        print("\n✅ Permisos y roles inicializados correctamente")
        print("\n📝 Para asignar un rol a un usuario:")
        print("   from app.services.permission_service import PermissionService")
        print("   svc = PermissionService(db)")
        print("   svc.assign_role_to_user(user_id=1, role_id=1)  # super_admin")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
