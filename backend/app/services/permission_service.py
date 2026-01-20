"""
PermissionService - Servicio de Permisos Granulares
===================================================
Verifica y gestiona permisos de usuarios.
ADITIVO: Nuevo servicio, no modifica existentes.
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List, Dict, Any, Set
from functools import lru_cache

from app.models.user import User
from app.models.permission import Permission, Role, role_permissions, user_role_assignments


class PermissionService:
    """Servicio de verificación de permisos"""

    def __init__(self, db: Session):
        self.db = db
        self._cache: Dict[int, Set[str]] = {}  # Cache local de permisos

    def get_user_permissions(self, user_id: int) -> Set[str]:
        """
        Obtiene todos los permisos de un usuario.
        Combina permisos de todos sus roles.

        Returns:
            Set de códigos de permiso: {"repairs:read", "clients:update", ...}
        """
        # Verificar cache
        if user_id in self._cache:
            return self._cache[user_id]

        # Obtener usuario con roles
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return set()

        permissions = set()

        # Permisos del rol legacy (role_id en users)
        legacy_permissions = self._get_legacy_role_permissions(user.role_id)
        permissions.update(legacy_permissions)

        # Permisos de roles asignados (tabla user_role_assignments)
        if hasattr(user, 'assigned_roles') and user.assigned_roles:
            for role in user.assigned_roles:
                if role.is_active:
                    for perm in role.permissions:
                        if perm.is_active:
                            permissions.add(perm.code)

        # Guardar en cache
        self._cache[user_id] = permissions
        return permissions

    def _get_legacy_role_permissions(self, role_id: int) -> Set[str]:
        """
        Mapea role_id legacy a permisos.
        Mantiene compatibilidad con sistema existente.

        role_id mapping:
        1 = admin -> todos los permisos
        2 = technician -> permisos de técnico
        3 = client -> solo lectura básica
        """
        if role_id == 1:  # Admin
            return {
                # Repairs
                "repairs:read", "repairs:create", "repairs:update", "repairs:delete",
                "repairs:update_status", "repairs:assign",
                # Clients
                "clients:read", "clients:create", "clients:update", "clients:delete",
                # Appointments
                "appointments:read", "appointments:create", "appointments:update", "appointments:delete",
                # Inventory
                "inventory:read", "inventory:create", "inventory:update", "inventory:delete",
                "inventory:adjust_stock",
                # Invoices
                "invoices:read", "invoices:create", "invoices:update", "invoices:void",
                # Quotes
                "quotes:read", "quotes:create", "quotes:update", "quotes:approve",
                # Tools
                "tools:read", "tools:create", "tools:update", "tools:calibrate",
                # Users
                "users:read", "users:create", "users:update", "users:delete", "users:manage_roles",
                # Reports
                "reports:read", "reports:export",
                # Settings
                "settings:read", "settings:update",
                # Warranties
                "warranties:read", "warranties:create", "warranties:update", "warranties:void",
                "warranties:evaluate_claim",
            }
        elif role_id == 2:  # Technician
            return {
                "repairs:read", "repairs:update", "repairs:update_status",
                "clients:read",
                "inventory:read", "inventory:adjust_stock",
                "tools:read", "tools:calibrate",
                "quotes:read",
                "warranties:read",
            }
        else:  # Client o cualquier otro
            return {
                "repairs:read",  # Solo sus propias reparaciones
                "appointments:read",
                "quotes:read",
                "invoices:read",
            }

    def has_permission(self, user_id: int, resource: str, action: str) -> bool:
        """
        Verifica si usuario tiene un permiso específico.

        Args:
            user_id: ID del usuario
            resource: Recurso (repairs, clients, etc.)
            action: Acción (read, create, update, delete, etc.)

        Returns:
            True si tiene permiso
        """
        permissions = self.get_user_permissions(user_id)
        permission_code = f"{resource}:{action}"

        # Verificar permiso exacto
        if permission_code in permissions:
            return True

        # Verificar wildcard (resource:*)
        wildcard = f"{resource}:*"
        if wildcard in permissions:
            return True

        # Super admin tiene todo
        if "*:*" in permissions:
            return True

        return False

    def has_any_permission(self, user_id: int, resource: str) -> bool:
        """Verifica si usuario tiene algún permiso sobre un recurso"""
        permissions = self.get_user_permissions(user_id)

        for perm in permissions:
            if perm.startswith(f"{resource}:") or perm == "*:*":
                return True
        return False

    def require_permissions(
        self,
        user_id: int,
        required: List[tuple]
    ) -> Dict[str, bool]:
        """
        Verifica múltiples permisos.

        Args:
            user_id: ID del usuario
            required: Lista de (resource, action)

        Returns:
            Dict con resultado por permiso
        """
        results = {}
        for resource, action in required:
            code = f"{resource}:{action}"
            results[code] = self.has_permission(user_id, resource, action)
        return results

    def clear_cache(self, user_id: Optional[int] = None):
        """Limpia cache de permisos"""
        if user_id:
            self._cache.pop(user_id, None)
        else:
            self._cache.clear()

    # =========================================================================
    # GESTIÓN DE ROLES (CRUD)
    # =========================================================================

    def get_role(self, role_id: int) -> Optional[Role]:
        """Obtiene un rol por ID"""
        return self.db.query(Role).filter(Role.id == role_id).first()

    def get_role_by_name(self, name: str) -> Optional[Role]:
        """Obtiene un rol por nombre"""
        return self.db.query(Role).filter(Role.name == name).first()

    def list_roles(self, include_inactive: bool = False) -> List[Role]:
        """Lista todos los roles"""
        query = self.db.query(Role)
        if not include_inactive:
            query = query.filter(Role.is_active == True)
        return query.all()

    def create_role(
        self,
        name: str,
        display_name: str,
        description: Optional[str] = None,
        permission_codes: Optional[List[str]] = None
    ) -> Role:
        """Crea un nuevo rol"""
        role = Role(
            name=name,
            display_name=display_name,
            description=description,
            is_system=False
        )

        if permission_codes:
            permissions = self.db.query(Permission).filter(
                Permission.is_active == True
            ).all()

            for perm in permissions:
                if perm.code in permission_codes or f"{perm.resource}:*" in permission_codes:
                    role.permissions.append(perm)

        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role

    def assign_role_to_user(self, user_id: int, role_id: int):
        """Asigna un rol a un usuario"""
        user = self.db.query(User).filter(User.id == user_id).first()
        role = self.db.query(Role).filter(Role.id == role_id).first()

        if not user or not role:
            return False

        if role not in user.assigned_roles:
            user.assigned_roles.append(role)
            self.db.commit()
            self.clear_cache(user_id)

        return True

    def remove_role_from_user(self, user_id: int, role_id: int):
        """Remueve un rol de un usuario"""
        user = self.db.query(User).filter(User.id == user_id).first()
        role = self.db.query(Role).filter(Role.id == role_id).first()

        if not user or not role:
            return False

        if role in user.assigned_roles:
            user.assigned_roles.remove(role)
            self.db.commit()
            self.clear_cache(user_id)

        return True

    # =========================================================================
    # GESTIÓN DE PERMISOS
    # =========================================================================

    def list_permissions(self) -> List[Permission]:
        """Lista todos los permisos activos"""
        return self.db.query(Permission).filter(Permission.is_active == True).all()

    def get_permissions_by_resource(self, resource: str) -> List[Permission]:
        """Obtiene permisos de un recurso"""
        return self.db.query(Permission).filter(
            Permission.resource == resource,
            Permission.is_active == True
        ).all()

    def add_permission_to_role(self, role_id: int, permission_id: int):
        """Añade un permiso a un rol"""
        role = self.db.query(Role).filter(Role.id == role_id).first()
        perm = self.db.query(Permission).filter(Permission.id == permission_id).first()

        if not role or not perm:
            return False

        if perm not in role.permissions:
            role.permissions.append(perm)
            self.db.commit()
            # Limpiar cache de todos los usuarios con este rol
            for user in role.users:
                self.clear_cache(user.id)

        return True

    def remove_permission_from_role(self, role_id: int, permission_id: int):
        """Remueve un permiso de un rol"""
        role = self.db.query(Role).filter(Role.id == role_id).first()
        perm = self.db.query(Permission).filter(Permission.id == permission_id).first()

        if not role or not perm:
            return False

        if perm in role.permissions:
            role.permissions.remove(perm)
            self.db.commit()
            # Limpiar cache
            for user in role.users:
                self.clear_cache(user.id)

        return True

    # =========================================================================
    # INICIALIZACIÓN
    # =========================================================================

    def init_default_permissions(self):
        """Inicializa permisos predefinidos si no existen"""
        from app.models.permission import DEFAULT_PERMISSIONS

        for resource, action, description in DEFAULT_PERMISSIONS:
            exists = self.db.query(Permission).filter(
                Permission.resource == resource,
                Permission.action == action
            ).first()

            if not exists:
                perm = Permission(
                    resource=resource,
                    action=action,
                    description=description
                )
                self.db.add(perm)

        self.db.commit()

    def init_default_roles(self):
        """Inicializa roles predefinidos si no existen"""
        from app.models.permission import DEFAULT_ROLES

        all_permissions = {p.code: p for p in self.list_permissions()}

        for role_name, config in DEFAULT_ROLES.items():
            exists = self.db.query(Role).filter(Role.name == role_name).first()

            if not exists:
                role = Role(
                    name=role_name,
                    display_name=config["display_name"],
                    description=config["description"],
                    is_system=config.get("is_system", False)
                )

                # Asignar permisos
                perm_specs = config.get("permissions", [])
                if perm_specs == "*":
                    # Todos los permisos
                    role.permissions = list(all_permissions.values())
                else:
                    for spec in perm_specs:
                        if spec.endswith(":*"):
                            # Wildcard: añadir todos los permisos del recurso
                            resource = spec.replace(":*", "")
                            for code, perm in all_permissions.items():
                                if perm.resource == resource:
                                    role.permissions.append(perm)
                        elif spec in all_permissions:
                            role.permissions.append(all_permissions[spec])

                self.db.add(role)

        self.db.commit()
