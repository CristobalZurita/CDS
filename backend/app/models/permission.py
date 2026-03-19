"""
Modelo Permission y Role para control de acceso granular
========================================================
Sistema de permisos por recurso y acción.
ADITIVO: No modifica tablas existentes.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


# Tabla de asociación Role <-> Permission (many-to-many)
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow)
)

# Tabla de asociación User <-> Role (many-to-many)
# Nota: Se llama 'user_role_assignments' para no conflictuar con 'user_roles' existente
user_role_assignments = Table(
    'user_role_assignments',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow)
)


class Permission(Base):
    """
    Permiso granular por recurso y acción.

    Ejemplos:
    - resource='repairs', action='read' -> Ver reparaciones
    - resource='repairs', action='update_status' -> Cambiar estado
    - resource='invoices', action='create' -> Crear facturas
    - resource='clients', action='delete' -> Eliminar clientes
    """
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    resource = Column(String(50), nullable=False, index=True)  # repairs, clients, invoices, etc.
    action = Column(String(50), nullable=False)  # read, create, update, delete, update_status, etc.
    description = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relación con roles
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")

    def __repr__(self):
        return f"<Permission({self.resource}:{self.action})>"

    @property
    def code(self):
        """Código único del permiso: resource:action"""
        return f"{self.resource}:{self.action}"


class Role(Base):
    """
    Rol de usuario con conjunto de permisos.

    Roles predefinidos:
    - super_admin: Todos los permisos
    - admin: Gestión completa excepto configuración sistema
    - technician: Reparaciones, diagnósticos, inventario básico
    - receptionist: Clientes, citas, cotizaciones
    - viewer: Solo lectura
    """
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=True)
    description = Column(String(255), nullable=True)
    is_system = Column(Boolean, default=False)  # Roles del sistema no se pueden eliminar
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    users = relationship("User", secondary=user_role_assignments, back_populates="assigned_roles")

    def __repr__(self):
        return f"<Role({self.name})>"

    def has_permission(self, resource: str, action: str) -> bool:
        """Verifica si el rol tiene un permiso específico"""
        for perm in self.permissions:
            if perm.resource == resource and perm.action == action and perm.is_active:
                return True
        return False

    def has_any_permission(self, resource: str) -> bool:
        """Verifica si el rol tiene algún permiso sobre un recurso"""
        for perm in self.permissions:
            if perm.resource == resource and perm.is_active:
                return True
        return False


# Permisos predefinidos para inicialización
DEFAULT_PERMISSIONS = [
    # Repairs
    ("repairs", "read", "Ver reparaciones"),
    ("repairs", "create", "Crear reparaciones"),
    ("repairs", "update", "Actualizar reparaciones"),
    ("repairs", "delete", "Eliminar reparaciones"),
    ("repairs", "update_status", "Cambiar estado de reparaciones"),
    ("repairs", "assign", "Asignar técnico a reparaciones"),

    # Clients
    ("clients", "read", "Ver clientes"),
    ("clients", "create", "Crear clientes"),
    ("clients", "update", "Actualizar clientes"),
    ("clients", "delete", "Eliminar clientes"),

    # Appointments
    ("appointments", "read", "Ver citas"),
    ("appointments", "create", "Crear citas"),
    ("appointments", "update", "Actualizar citas"),
    ("appointments", "delete", "Eliminar citas"),

    # Inventory
    ("inventory", "read", "Ver inventario"),
    ("inventory", "create", "Crear productos"),
    ("inventory", "update", "Actualizar productos"),
    ("inventory", "delete", "Eliminar productos"),
    ("inventory", "adjust_stock", "Ajustar stock"),

    # Invoices
    ("invoices", "read", "Ver facturas"),
    ("invoices", "create", "Crear facturas"),
    ("invoices", "update", "Actualizar facturas"),
    ("invoices", "void", "Anular facturas"),

    # Quotes
    ("quotes", "read", "Ver cotizaciones"),
    ("quotes", "create", "Crear cotizaciones"),
    ("quotes", "update", "Actualizar cotizaciones"),
    ("quotes", "approve", "Aprobar cotizaciones"),

    # Tools
    ("tools", "read", "Ver herramientas"),
    ("tools", "create", "Crear herramientas"),
    ("tools", "update", "Actualizar herramientas"),
    ("tools", "calibrate", "Registrar calibración"),

    # Users
    ("users", "read", "Ver usuarios"),
    ("users", "create", "Crear usuarios"),
    ("users", "update", "Actualizar usuarios"),
    ("users", "delete", "Eliminar usuarios"),
    ("users", "manage_roles", "Gestionar roles de usuarios"),

    # Reports
    ("reports", "read", "Ver reportes"),
    ("reports", "export", "Exportar reportes"),

    # Settings
    ("settings", "read", "Ver configuración"),
    ("settings", "update", "Actualizar configuración"),

    # Diagnostics
    ("diagnostics", "read", "Ver diagnósticos"),
    ("diagnostics", "create", "Crear diagnósticos"),
    ("diagnostics", "update", "Actualizar diagnósticos"),
    ("diagnostics", "delete", "Eliminar diagnósticos"),

    # Payments
    ("payments", "read", "Ver pagos"),
    ("payments", "create", "Registrar pagos"),

    # Media
    ("media", "read", "Ver catálogo de medios"),
    ("media", "create", "Registrar/importar medios"),
    ("media", "update", "Actualizar bindings de medios"),
    ("media", "delete", "Eliminar medios o bindings"),

    # Repair Statuses
    ("repair_statuses", "read", "Ver estados de reparación"),
    ("repair_statuses", "create", "Crear estados de reparación"),
    ("repair_statuses", "update", "Actualizar estados de reparación"),
    ("repair_statuses", "delete", "Eliminar estados de reparación"),

    # Stock Movements
    ("stock_movements", "read", "Ver movimientos de stock"),
    ("stock_movements", "create", "Registrar movimientos de stock"),

    # Instruments
    ("instruments", "read", "Ver instrumentos"),
    ("instruments", "create", "Crear instrumentos"),
    ("instruments", "update", "Actualizar instrumentos"),
    ("instruments", "delete", "Eliminar instrumentos"),

    # Newsletter
    ("newsletter", "read", "Ver suscripciones al newsletter"),

    # Categories
    ("categories", "read", "Ver categorías"),
    ("categories", "create", "Crear categorías"),
    ("categories", "update", "Actualizar categorías"),
    ("categories", "delete", "Eliminar categorías"),

    # Devices
    ("devices", "read", "Ver dispositivos"),
    ("devices", "create", "Crear dispositivos"),
    ("devices", "update", "Actualizar dispositivos"),
    ("devices", "delete", "Eliminar dispositivos"),

    # Contact Messages
    ("contact_messages", "read", "Ver mensajes de contacto"),

    # Tickets
    ("tickets", "read", "Ver tickets"),
    ("tickets", "create", "Crear tickets"),
    ("tickets", "update", "Actualizar tickets"),
    ("tickets", "delete", "Eliminar tickets"),

    # Purchase Requests (carrito interno)
    ("purchase_requests", "read", "Ver solicitudes de compra"),
    ("purchase_requests", "create", "Crear solicitudes de compra"),
    ("purchase_requests", "update", "Actualizar solicitudes de compra"),
    ("purchase_requests", "delete", "Eliminar solicitudes de compra"),

    # Manuals
    ("manuals", "read", "Ver manuales"),
    ("manuals", "create", "Crear manuales"),
    ("manuals", "update", "Actualizar manuales"),
    ("manuals", "delete", "Eliminar manuales"),

    # Signatures
    ("signatures", "read", "Ver firmas"),
    ("signatures", "create", "Crear solicitudes de firma"),

    # Warranties
    ("warranties", "read", "Ver garantías"),
    ("warranties", "create", "Crear garantías"),
    ("warranties", "void", "Anular garantías"),
    ("warranties", "evaluate_claim", "Evaluar reclamos de garantía"),
]

# Roles predefinidos con sus permisos
DEFAULT_ROLES = {
    "super_admin": {
        "display_name": "Super Administrador",
        "description": "Acceso completo al sistema",
        "is_system": True,
        "permissions": "*"  # Todos los permisos
    },
    "admin": {
        "display_name": "Administrador",
        "description": "Gestión completa excepto configuración del sistema",
        "is_system": True,
        "permissions": [
            "repairs:*", "clients:*", "appointments:*", "inventory:*",
            "invoices:*", "quotes:*", "tools:*", "users:read", "users:update",
            "reports:*", "media:*"
        ]
    },
    "technician": {
        "display_name": "Técnico",
        "description": "Reparaciones, diagnósticos e inventario básico",
        "is_system": True,
        "permissions": [
            "repairs:read", "repairs:update", "repairs:update_status",
            "clients:read",
            "inventory:read", "inventory:adjust_stock",
            "tools:read", "tools:calibrate",
            "quotes:read"
        ]
    },
    "receptionist": {
        "display_name": "Recepcionista",
        "description": "Clientes, citas y cotizaciones",
        "is_system": True,
        "permissions": [
            "repairs:read", "repairs:create",
            "clients:read", "clients:create", "clients:update",
            "appointments:*",
            "quotes:read", "quotes:create",
            "invoices:read"
        ]
    },
    "viewer": {
        "display_name": "Solo Lectura",
        "description": "Acceso de solo lectura",
        "is_system": True,
        "permissions": [
            "repairs:read", "clients:read", "appointments:read",
            "inventory:read", "quotes:read", "invoices:read"
        ]
    }
}
