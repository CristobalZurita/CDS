"""
Modelo Product para inventario
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.core.database import Base


class Product(Base):
    """Producto en inventario (repuestos, componentes, etc.)"""
    
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    sku = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False)  # Precio en centavos
    quantity = Column(Integer, default=0, nullable=False)
    min_quantity = Column(Integer, default=5, nullable=False)  # Para alertas de stock bajo
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relaciones
    category = relationship("Category", back_populates="products")
    stock_movements = relationship("StockMovement", back_populates="product")
    
    @property
    def is_low_stock(self):
        """Retorna True si el stock está bajo"""
        return self.quantity <= self.min_quantity
    
    def __repr__(self):
        return f"<Product(id={self.id}, sku={self.sku}, quantity={self.quantity})>"
