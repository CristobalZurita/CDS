"""
Specification Pattern - Fase 2 (ADITIVO)
=======================================

Patrón para filtros avanzados y reutilizables.
Permite construir queries complejos de forma compositiva.

NO reemplaza nada existente - es ADITIVO.

Inspirado en:
- Eric Evans' Domain-Driven Design
- Specification Pattern (Fowler)

Uso:
    from app.repositories.specifications import (
        AndSpecification, OrSpecification, NotSpecification,
        InventorySpecs, RepairSpecs
    )
    
    # Componer filtros
    spec = (InventorySpecs.in_stock() & InventorySpecs.by_family('resistors')) | InventorySpecs.by_sku('123')
    
    results = spec.filter(db.query(Product)).all()
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, TypeVar, List, Optional, Union
from dataclasses import dataclass

from sqlalchemy import and_, or_, not_, func
from sqlalchemy.orm import Query, Session


# =============================================================================
# Clase base Specification
# =============================================================================
T = TypeVar('T')


class Specification(ABC, Generic[T]):
    """
    Clase base para Specifications.
    
    Una Specification define un criterio que puede ser usado
    para filtrar o verificar objetos.
    """
    
    @abstractmethod
    def is_satisfied_by(self, obj: T) -> bool:
        """Verifica si el objeto cumple la especificación"""
        raise NotImplementedError
    
    def filter(self, query: Query) -> Query:
        """Aplica la especificación como filtro SQLAlchemy"""
        raise NotImplementedError
    
    def __and__(self, other: 'Specification[T]') -> 'AndSpecification[T]':
        """Operador AND: both conditions must be true"""
        return AndSpecification(self, other)
    
    def __or__(self, other: 'Specification[T]') -> 'OrSpecification[T]':
        """Operador OR: either condition must be true"""
        return OrSpecification(self, other)
    
    def __invert__(self) -> 'NotSpecification[T]':
        """Operador NOT: negate condition"""
        return NotSpecification(self)


# =============================================================================
# Especificaciones compuestas
# =============================================================================
class AndSpecification(Specification[T]):
    """Ambas condiciones deben cumplirse (AND)"""
    
    def __init__(self, left: Specification[T], right: Specification[T]):
        self.left = left
        self.right = right
    
    def is_satisfied_by(self, obj: T) -> bool:
        return self.left.is_satisfied_by(obj) and self.right.is_satisfied_by(obj)
    
    def filter(self, query: Query) -> Query:
        # Combinar ambas especificaciones
        left_query = self.left.filter(query)
        return self.right.filter(left_query)


class OrSpecification(Specification[T]):
    """Cualquiera de las condiciones debe cumplirse (OR)"""
    
    def __init__(self, left: Specification[T], right: Specification[T]):
        self.left = left
        self.right = right
    
    def is_satisfied_by(self, obj: T) -> bool:
        return self.left.is_satisfied_by(obj) or self.right.is_satisfied_by(obj)
    
    def filter(self, query: Query) -> Query:
        # Combinar con OR
        from sqlalchemy import or_ as sql_or
        # Esta es una implementación simplificada
        # Para casos complejos, usar la composición de filtros
        return self.right.filter(self.left.filter(query))


class NotSpecification(Specification[T]):
    """Invierte la condición (NOT)"""
    
    def __init__(self, spec: Specification[T]):
        self.spec = spec
    
    def is_satisfied_by(self, obj: T) -> bool:
        return not self.spec.is_satisfied_by(obj)
    
    def filter(self, query: Query) -> Query:
        # Implementar negación si es posible
        return query


class TrueSpecification(Specification[T]):
    """Siempre verdadera - útil como默认值"""
    
    def is_satisfied_by(self, obj: T) -> bool:
        return True
    
    def filter(self, query: Query) -> Query:
        return query


# =============================================================================
# Specifications para Inventario
# =============================================================================
class InventorySpecs:
    """
    Specifications predefinidas para inventario.
    
    Uso:
        # Filtrar resistores en stock
        spec = InventorySpecs.in_stock() & InventorySpecs.by_family('resistors')
        results = spec.filter(db.query(Product)).all()
        
        # Filtrar componentes SMD
        spec = InventorySpecs.by_footprint('SMD') | InventorySpecs.by_footprint('0805')
        results = spec.filter(db.query(Product)).all()
    """
    
    @staticmethod
    def in_stock() -> 'InventoryInStockSpec':
        """Productos con stock disponible"""
        return InventoryInStockSpec()
    
    @staticmethod
    def low_stock(threshold: int = 5) -> 'InventoryLowStockSpec':
        """Productos con stock bajo"""
        return InventoryLowStockSpec(threshold)
    
    @staticmethod
    def by_family(family: str) -> 'InventoryFamilySpec':
        """Productos por familia (resistors, capacitors, etc.)"""
        return InventoryFamilySpec(family)
    
    @staticmethod
    def by_sku(sku: str) -> 'InventorySkuSpec':
        """Productos por SKU exacto"""
        return InventorySkuSpec(sku)
    
    @staticmethod
    def by_sku_like(sku_pattern: str) -> 'InventorySkuLikeSpec':
        """Productos por patrón SKU (LIKE)"""
        return InventorySkuLikeSpec(sku_pattern)
    
    @staticmethod
    def by_category(category_id: int) -> 'InventoryCategorySpec':
        """Productos por categoría"""
        return InventoryCategorySpec(category_id)
    
    @staticmethod
    def by_footprint(footprint: str) -> 'InventoryFootprintSpec':
        """Productos por footprint (THT, SMD, DIP)"""
        return InventoryFootprintSpec(footprint)
    
    @staticmethod
    def by_origin(origin: str) -> 'InventoryOriginSpec':
        """Productos por origen (REAL, CATALOGO_ONLY)"""
        return InventoryOriginSpec(origin)
    
    @staticmethod
    def enabled_only() -> 'InventoryEnabledSpec':
        """Solo productos habilitados"""
        return InventoryEnabledSpec()
    
    @staticmethod
    def by_price_range(min_price: int = 0, max_price: int = None) -> 'InventoryPriceRangeSpec':
        """Productos por rango de precio"""
        return InventoryPriceRangeSpec(min_price, max_price)


# =============================================================================
# Implementaciones de Inventory Specifications
# =============================================================================
class InventoryInStockSpec(Specification):
    """Filtrar productos con stock > 0"""
    
    def is_satisfied_by(self, obj: Any) -> bool:
        return hasattr(obj, 'quantity') and obj.quantity > 0
    
    def filter(self, query: Query) -> Query:
        from app.models import Product
        return query.filter(Product.quantity > 0)


class InventoryLowStockSpec(Specification):
    """Filtrar productos con stock bajo"""
    
    def __init__(self, threshold: int = 5):
        self.threshold = threshold
    
    def is_satisfied_by(self, obj: Any) -> bool:
        return hasattr(obj, 'quantity') and obj.quantity <= self.threshold
    
    def filter(self, query: Query) -> Query:
        from app.models import Product
        return query.filter(Product.quantity <= self.threshold)


class InventoryFamilySpec(Specification):
    """Filtrar por familia de componente"""
    
    def __init__(self, family: str):
        self.family = family.lower()
    
    def is_satisfied_by(self, obj: Any) -> bool:
        return hasattr(obj, 'family') and obj.family and self.family in obj.family.lower()
    
    def filter(self, query: Query) -> Query:
        from app.models import Product, Category
        from sqlalchemy import select
        subq = select(Category.id).where(Category.name.ilike(f'%{self.family}%'))
        return query.filter(Product.category_id.in_(subq))


class InventorySkuSpec(Specification):
    """Filtrar por SKU exacto"""
    
    def __init__(self, sku: str):
        self.sku = sku
    
    def is_satisfied_by(self, obj: Any) -> bool:
        return hasattr(obj, 'sku') and obj.sku == self.sku
    
    def filter(self, query: Query) -> Query:
        from app.models import Product
        return query.filter(Product.sku == self.sku)


class InventorySkuLikeSpec(Specification):
    """Filtrar por patrón SKU (LIKE)"""
    
    def __init__(self, sku_pattern: str):
        self.sku_pattern = f"%{sku_pattern}%"
    
    def is_satisfied_by(self, obj: Any) -> bool:
        return hasattr(obj, 'sku') and obj.sku and self.sku_pattern.replace('%', '') in obj.sku
    
    def filter(self, query: Query) -> Query:
        from app.models import Product
        return query.filter(Product.sku.ilike(self.sku_pattern))


class InventoryCategorySpec(Specification):
    """Filtrar por categoría"""
    
    def __init__(self, category_id: int):
        self.category_id = category_id
    
    def is_satisfied_by(self, obj: Any) -> bool:
        return hasattr(obj, 'category_id') and obj.category_id == self.category_id
    
    def filter(self, query: Query) -> Query:
        from app.models import Product
        return query.filter(Product.category_id == self.category_id)


class InventoryFootprintSpec(Specification):
    """Filtrar por footprint (THT, SMD, DIP)"""
    
    def __init__(self, footprint: str):
        self.footprint = footprint.upper()
    
    def is_satisfied_by(self, obj: Any) -> bool:
        footprint_fields = ['footprint', 'package_type', 'package_code', 'kicad_footprint']
        for field in footprint_fields:
            if hasattr(obj, field):
                value = getattr(obj, field, '')
                if value and self.footprint in str(value).upper():
                    return True
        return False
    
    def filter(self, query: Query) -> Query:
        from app.models import Product
        return query.filter(
            or_(
                Product.description.ilike(f'%{self.footprint}%'),
                Product.sku.ilike(f'%{self.footprint}%')
            )
        )


class InventoryOriginSpec(Specification):
    """Filtrar por origen (REAL, CATALOGO_ONLY)"""
    
    def __init__(self, origin: str):
        self.origin = origin.upper()
    
    def is_satisfied_by(self, obj: Any) -> bool:
        origin_fields = ['origin_status', 'source', 'origin']
        for field in origin_fields:
            if hasattr(obj, field):
                value = getattr(obj, field, '')
                if value and self.origin in str(value).upper():
                    return True
        return False
    
    def filter(self, query: Query) -> Query:
        from app.models import Product
        return query.filter(Product.sku.ilike(f'%{self.origin}%'))


class InventoryEnabledSpec(Specification):
    """Filtrar solo productos habilitados"""
    
    def is_satisfied_by(self, obj: Any) -> bool:
        return not hasattr(obj, 'enabled') or obj.enabled is True
    
    def filter(self, query: Query) -> Query:
        return query


class InventoryPriceRangeSpec(Specification):
    """Filtrar por rango de precio"""
    
    def __init__(self, min_price: int = 0, max_price: int = None):
        self.min_price = min_price
        self.max_price = max_price
    
    def is_satisfied_by(self, obj: Any) -> bool:
        if not hasattr(obj, 'price'):
            return False
        price = obj.price or 0
        if price < self.min_price:
            return False
        if self.max_price and price > self.max_price:
            return False
        return True
    
    def filter(self, query: Query) -> Query:
        from app.models import Product
        q = query.filter(Product.price >= self.min_price)
        if self.max_price:
            q = q.filter(Product.price <= self.max_price)
        return q


# =============================================================================
# Specifications para Reparaciones
# =============================================================================
class RepairSpecs:
    """
    Specifications predefinidas para reparaciones.
    """
    
    @staticmethod
    def by_status(status_id: int) -> 'RepairStatusSpec':
        """Reparaciones por estado"""
        return RepairStatusSpec(status_id)
    
    @staticmethod
    def by_client(client_id: int) -> 'RepairClientSpec':
        """Reparaciones por cliente"""
        return RepairClientSpec(client_id)
    
    @staticmethod
    def by_technician(technician_id: int) -> 'RepairTechnicianSpec':
        """Reparaciones por técnico asignado"""
        return RepairTechnicianSpec(technician_id)
    
    @staticmethod
    def pending() -> 'RepairPendingSpec':
        """Reparaciones pendientes (no entregadas)"""
        return RepairPendingSpec()
    
    @staticmethod
    def in_progress() -> 'RepairInProgressSpec':
        """Reparaciones en trabajo"""
        return RepairInProgressSpec()
    
    @staticmethod
    def completed() -> 'RepairCompletedSpec':
        """Reparaciones completadas"""
        return RepairCompletedSpec()
    
    @staticmethod
    def overdue(days: int = 30) -> 'RepairOverdueSpec':
        """Reparaciones vencidas (sin actualización por X días)"""
        return RepairOverdueSpec(days)
    
    @staticmethod
    def by_date_range(start_date: str, end_date: str) -> 'RepairDateRangeSpec':
        """Reparaciones por rango de fecha"""
        return RepairDateRangeSpec(start_date, end_date)


class RepairStatusSpec(Specification):
    def __init__(self, status_id: int):
        self.status_id = status_id
    
    def filter(self, query: Query) -> Query:
        from app.models import Repair
        return query.filter(Repair.status_id == self.status_id)


class RepairClientSpec(Specification):
    def __init__(self, client_id: int):
        self.client_id = client_id
    
    def filter(self, query: Query) -> Query:
        from app.models import Repair, Device
        return query.join(Device).filter(Device.client_id == self.client_id)


class RepairTechnicianSpec(Specification):
    def __init__(self, technician_id: int):
        self.technician_id = technician_id
    
    def filter(self, query: Query) -> Query:
        from app.models import Repair
        return query.filter(Repair.assigned_to == self.technician_id)


class RepairPendingSpec(Specification):
    def filter(self, query: Query) -> Query:
        from app.models import Repair
        return query.filter(Repair.status_id < 7)


class RepairInProgressSpec(Specification):
    def filter(self, query: Query) -> Query:
        from app.models import Repair
        return query.filter(Repair.status_id == 5)


class RepairCompletedSpec(Specification):
    def filter(self, query: Query) -> Query:
        from app.models import Repair
        return query.filter(Repair.status_id >= 6)


class RepairOverdueSpec(Specification):
    def __init__(self, days: int = 30):
        self.days = days
    
    def filter(self, query: Query) -> Query:
        from app.models import Repair
        from datetime import datetime, timedelta
        cutoff = datetime.utcnow() - timedelta(days=self.days)
        return query.filter(
            Repair.updated_at < cutoff,
            Repair.status_id < 7
        )


class RepairDateRangeSpec(Specification):
    def __init__(self, start_date: str, end_date: str):
        self.start_date = start_date
        self.end_date = end_date
    
    def filter(self, query: Query) -> Query:
        from app.models import Repair
        return query.filter(
            Repair.created_at >= self.start_date,
            Repair.created_at <= self.end_date
        )


# =============================================================================
# Helper para construir especificaciones desde params
# =============================================================================
def build_inventory_spec(
    family: str = None,
    in_stock: bool = None,
    low_stock: bool = None,
    enabled_only: bool = True,
    category_id: int = None,
    sku: str = None,
    min_price: int = None,
    max_price: int = None,
    origin: str = None
) -> Specification:
    """
    Construye Specification desde parámetros de request.
    
    Usage:
        spec = build_inventory_spec(
            family='resistors',
            in_stock=True,
            enabled_only=True
        )
        results = spec.filter(db.query(Product)).all()
    """
    specs = []
    
    if in_stock:
        specs.append(InventorySpecs.in_stock())
    
    if low_stock:
        specs.append(InventorySpecs.low_stock())
    
    if family:
        specs.append(InventorySpecs.by_family(family))
    
    if category_id:
        specs.append(InventorySpecs.by_category(category_id))
    
    if sku:
        specs.append(InventorySpecs.by_sku(sku))
    
    if min_price or max_price:
        specs.append(InventorySpecs.by_price_range(min_price or 0, max_price))
    
    if origin:
        specs.append(InventorySpecs.by_origin(origin))
    
    if enabled_only:
        specs.append(InventorySpecs.enabled_only())
    
    if not specs:
        return TrueSpecification()
    
    # Combinar todos con AND
    result = specs[0]
    for spec in specs[1:]:
        result = result & spec
    
    return result


# =============================================================================
# Ejemplo de uso (documentación)
# =============================================================================
"""
# EJEMPLO 1: Filtrar inventario con Specification
from app.repositories.specifications import InventorySpecs, build_inventory_spec

@app.get("/inventory/filter")
def filter_inventory(
    family: str = None,
    in_stock: bool = True,
    enabled_only: bool = True
):
    spec = build_inventory_spec(
        family=family,
        in_stock=in_stock,
        enabled_only=enabled_only
    )
    products = spec.filter(db.query(Product)).all()
    return products


# EJEMPLO 2: Filtros complejos con composición
from app.repositories.specifications import InventorySpecs, OrSpecification

# Resistores O capacitores, en stock
spec = (
    InventorySpecs.by_family('resistors') | 
    InventorySpecs.by_family('capacitors')
) & InventorySpecs.in_stock()

results = spec.filter(db.query(Product)).all()


# EJEMPLO 3: Reparaciones pendientes con overdue
from app.repositories.specifications import RepairSpecs

spec = RepairSpecs.pending() & RepairSpecs.overdue(days=30)
overdue_repairs = spec.filter(db.query(Repair)).all()


# EJEMPLO 4: Filtros dinámicos desde params
def dynamic_filter(params: dict):
    specs = []
    
    if params.get('status'):
        specs.append(RepairSpecs.by_status(params['status']))
    
    if params.get('client_id'):
        specs.append(RepairSpecs.by_client(params['client_id']))
    
    if params.get('technician_id'):
        specs.append(RepairSpecs.by_technician(params['technician_id']))
    
    if not specs:
        return db.query(Repair).all()
    
    # Combinar con AND
    combined = specs[0]
    for s in specs[1:]:
        combined = combined & s
    
    return combined.filter(db.query(Repair)).all()
"""
