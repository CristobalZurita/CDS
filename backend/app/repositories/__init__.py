"""
Repositories Module - ADITIVO
============================

Contiene:
- base_repository.py: Repositorio base genérico
- repair_repository.py: Repositorio de reparaciones
- category_repository.py: Repositorio de categorías
- unit_of_work.py: Unit of Work pattern (NUEVO)
- specifications.py: Specification pattern (NUEVO)
"""

from app.repositories.base_repository import BaseRepository
from app.repositories.repair_repository import RepairRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.unit_of_work import UnitOfWork, get_uow
from app.repositories.specifications import (
    Specification,
    AndSpecification,
    OrSpecification,
    NotSpecification,
    TrueSpecification,
    InventorySpecs,
    RepairSpecs,
    build_inventory_spec
)

__all__ = [
    # Base
    'BaseRepository',
    'RepairRepository',
    'CategoryRepository',
    
    # Unit of Work
    'UnitOfWork',
    'get_uow',
    
    # Specifications
    'Specification',
    'AndSpecification',
    'OrSpecification',
    'NotSpecification',
    'TrueSpecification',
    'InventorySpecs',
    'RepairSpecs',
    'build_inventory_spec'
]
