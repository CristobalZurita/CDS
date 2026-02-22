"""
Unit of Work Pattern - Fase 1 (ADITIVO)
========================================

Patrón para gestionar transacciones atómicas complejas.
Permite usar componentes + crear OT + pagos en una sola operación.

NO reemplaza nada existente - es ADITIVO.

Inspirado en:
- Fowler's Unit of Work
- SQLAlchemy's session management

Uso:
    from app.repositories.unit_of_work import UnitOfWork
    
    async with UnitOfWork(db) as uow:
        await uow.repairs.create(...)
        await uow.inventory.reserve(...)
        await uow.payments.create(...)
        # Commit automático al salir del context
"""

from __future__ import annotations

from typing import Any, Callable, Generic, TypeVar, Optional
from contextlib import asynccontextmanager
from dataclasses import dataclass, field

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import SessionLocal


# =============================================================================
# Tipos genéricos
# =============================================================================
T = TypeVar('T')


# =============================================================================
# Unit of Work Manager
# =============================================================================
class UnitOfWork:
    """
    Context manager para transacciones atómicas.
    
    Usage:
        async with UnitOfWork(db) as uow:
            repair = await uow.repairs.create(...)
            await uow.inventory.reserve_component(...)
            await uow.payments.process_deposit(...)
            # Auto-commit al salir del context
    """
    
    def __init__(self, db: Session):
        self.db = db
        self._committed = False
        self._rolled_back = False
        
        # Repositorios disponibles
        self.repairs: Optional[RepairRepositoryUnit] = None
        self.inventory: Optional[InventoryRepositoryUnit] = None
        self.payments: Optional[PaymentRepositoryUnit] = None
        self.clients: Optional[ClientRepositoryUnit] = None
        
        # Inicializar repositorios
        self._init_repositories()
    
    def _init_repositories(self):
        """Inicializa repositorios con esta sesión"""
        self.repairs = RepairRepositoryUnit(self.db)
        self.inventory = InventoryRepositoryUnit(self.db)
        self.payments = PaymentRepositoryUnit(self.db)
        self.clients = ClientRepositoryUnit(self.db)
    
    def __enter__(self) -> 'UnitOfWork':
        """Entrada del context manager (sync)"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """
        Salida del context manager.
        - Si excepción: hace rollback
        - Si no: hace commit automáticamente
        """
        if exc_type is not None:
            # Excepción ocurrida - rollback
            self.db.rollback()
            self._rolled_back = True
            return False  # Re-raise la excepción
        
        # Sin excepción - commit automático
        if not self._committed and not self._rolled_back:
            try:
                self.db.commit()
                self._committed = True
            except Exception as e:
                self.db.rollback()
                self._rolled_back = True
                raise
        
        return False
    
    async def __aenter__(self) -> 'UnitOfWork':
        """Entrada async del context manager"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Salida async del context manager"""
        return self.__exit__(exc_type, exc_val, exc_tb)
    
    def rollback(self) -> None:
        """Force rollback manual"""
        self.db.rollback()
        self._rolled_back = True
        self._committed = False
    
    def commit(self) -> None:
        """Force commit manual"""
        if not self._rolled_back:
            self.db.commit()
            self._committed = True


# =============================================================================
# Repositorios Unit of Work (usan la misma sesión)
# =============================================================================
class RepairRepositoryUnit:
    """Repositorio de reparaciones para Unit of Work"""
    
    def __init__(self, db: Session):
        self.db = db
        from app.models import Repair, RepairComponentUsage
        from app.crud.base import CRUDBase
        self._crud = CRUDBase(Repair)
        self._component_model = RepairComponentUsage
    
    async def create(self, **kwargs) -> Any:
        """Crear reparación"""
        repair = self._crud.create(self.db, kwargs)
        return repair
    
    async def update(self, repair_id: int, **kwargs) -> Any:
        """Actualizar reparación"""
        repair = self._crud.get(self.db, repair_id)
        if not repair:
            raise ValueError(f"Repair {repair_id} not found")
        return self._crud.update(self.db, repair, kwargs)
    
    async def add_component_usage(self, repair_id: int, component_data: dict) -> Any:
        """Agregar componente usado"""
        from app.models import RepairComponentUsage
        usage = RepairComponentUsage(
            repair_id=repair_id,
            component_table=component_data.get('component_table', 'products'),
            component_id=component_data.get('component_id'),
            quantity=component_data.get('quantity', 1),
            unit_cost=component_data.get('unit_cost'),
            notes=component_data.get('notes')
        )
        self.db.add(usage)
        self.db.flush()
        return usage
    
    async def get(self, repair_id: int) -> Any:
        """Obtener reparación por ID"""
        return self._crud.get(self.db, repair_id)


class InventoryRepositoryUnit:
    """Repositorio de inventario para Unit of Work"""
    
    def __init__(self, db: Session):
        self.db = db
        from app.models import Stock
        from app.models import StockMovement
        self._stock_model = Stock
        self._movement_model = StockMovement
    
    async def reserve_component(self, product_id: int, quantity: int) -> bool:
        """
        Reservar componente del inventario.
        Decrementa stock disponible.
        """
        from app.models import Stock
        stock = self.db.query(Stock).filter(
            Stock.product_id == product_id
        ).first()
        
        if not stock or stock.quantity < quantity:
            raise ValueError(f"Insufficient stock for product {product_id}")
        
        stock.quantity -= quantity
        self.db.add(stock)
        self.db.flush()
        return True
    
    async def release_component(self, product_id: int, quantity: int) -> bool:
        """Liberar componente (rollback de reserva)"""
        from app.models import Stock
        stock = self.db.query(Stock).filter(
            Stock.product_id == product_id
        ).first()
        
        if stock:
            stock.quantity += quantity
            self.db.add(stock)
            self.db.flush()
        return True
    
    async def decrement_stock(self, product_id: int, quantity: int, reason: str, repair_id: int = None) -> bool:
        """
        Decrementar stock con tracking de movimiento.
        """
        from app.models import Stock, StockMovement
        
        stock = self.db.query(Stock).filter(
            Stock.product_id == product_id
        ).first()
        
        if not stock or stock.quantity < quantity:
            raise ValueError(f"Insufficient stock for product {product_id}")
        
        # Decrementar
        stock.quantity -= quantity
        self.db.add(stock)
        
        # Registrar movimiento
        movement = StockMovement(
            product_id=product_id,
            movement_type='decrement',
            quantity=quantity,
            reason=reason,
            repair_id=repair_id,
            created_by=None  # Se llenará desde contexto
        )
        self.db.add(movement)
        self.db.flush()
        
        return True


class PaymentRepositoryUnit:
    """Repositorio de pagos para Unit of Work"""
    
    def __init__(self, db: Session):
        self.db = db
        from app.models import Payment, PaymentStatus
        from app.crud.base import CRUDBase
        self._crud = CRUDBase(Payment)
        self._status_enum = PaymentStatus
    
    async def create(self, **kwargs) -> Any:
        """Crear pago"""
        return self._crud.create(self.db, kwargs)
    
    async def update_status(self, payment_id: int, status: str) -> Any:
        """Actualizar estado de pago"""
        from app.models import PaymentStatus
        payment = self._crud.get(self.db, payment_id)
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")
        
        status_map = {
            'pending': PaymentStatus.PENDING,
            'completed': PaymentStatus.COMPLETED,
            'failed': PaymentStatus.FAILED,
            'refunded': PaymentStatus.REFUNDED
        }
        
        payment.status = status_map.get(status, PaymentStatus.PENDING)
        self.db.add(payment)
        self.db.flush()
        return payment


class ClientRepositoryUnit:
    """Repositorio de clientes para Unit of Work"""
    
    def __init__(self, db: Session):
        self.db = db
        from app.models import Client
        from app.crud.base import CRUDBase
        self._crud = CRUDBase(Client)
    
    async def get_by_user_id(self, user_id: int) -> Any:
        """Obtener cliente por user_id"""
        from app.models import Client
        return self.db.query(Client).filter(Client.user_id == user_id).first()
    
    async def get(self, client_id: int) -> Any:
        """Obtener cliente por ID"""
        return self._crud.get(self.db, client_id)


# =============================================================================
# Helper para usar en endpoints existentes
# =============================================================================
def get_uow(db: Session) -> UnitOfWork:
    """Factory para crear Unit of Work con una sesión"""
    return UnitOfWork(db)


# =============================================================================
# Ejemplo de uso (documentación)
# =============================================================================
"""
# EJEMPLO 1: Crear OT con componentes y pago en una transacción
from app.repositories.unit_of_work import get_uow

@app.post("/repairs")
async def create_repair_with_all(db: Session = Depends(get_db)):
    async with get_uow(db) as uow:
        # 1. Crear reparación
        repair = await uow.repairs.create(
            device_id=payload.device_id,
            problem_reported=payload.problem_reported,
            status_id=1  # Ingreso
        )
        
        # 2. Reservar componentes (si hay)
        for comp in payload.components:
            await uow.inventory.reserve_component(comp.product_id, comp.quantity)
            await uow.repairs.add_component_usage(
                repair.id,
                {'component_id': comp.product_id, 'quantity': comp.quantity, 'unit_cost': comp.unit_cost}
            )
        
        # 3. Crear pago inicial si hay depósito
        if payload.deposit_amount:
            await uow.payments.create(
                repair_id=repair.id,
                amount=payload.deposit_amount,
                payment_type='deposit',
                status='pending'
            )
        
        # Auto-commit al salir del context
        return repair


# EJEMPLO 2: Rollback manual
async def process_repair_completion(db: Session, repair_id: int):
    uow = get_uow(db)
    try:
        async with uow:
            # Actualizar reparación
            repair = await uow.repairs.update(repair_id, status_id=6)  # Listo
            
            # Decrementar stock
            components = get_components_used(repair_id)
            for comp in components:
                await uow.inventory.decrement_stock(
                    comp.product_id, 
                    comp.quantity, 
                    'repair_completion',
                    repair_id
                )
            
            # Auto-commit
    except Exception as e:
        # Automatic rollback gracias al context manager
        raise HTTPException(status_code=500, detail=str(e))
"""
