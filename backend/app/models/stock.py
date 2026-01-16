"""
Modelo Stock para registro de inventario - Alineado con schema real de cirujano.db
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Stock(Base):
    """
    Registro de stock para componentes.
    Sistema polimórfico: component_table + component_id identifican el item.
    """

    __tablename__ = "stock"

    id = Column(Integer, primary_key=True, autoincrement=True)
    component_table = Column(String, nullable=False)
    component_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    quantity_reserved = Column(Integer, default=0)
    minimum_stock = Column(Integer, default=5)
    location_id = Column(Integer, ForeignKey("storage_locations.id"), nullable=True)
    bin_code = Column(String, nullable=True)
    supplier = Column(String, nullable=True)
    supplier_part_number = Column(String, nullable=True)
    unit_cost = Column(Float, nullable=True)
    last_purchase_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    movements = relationship("StockMovement", back_populates="stock")

    @property
    def is_low_stock(self):
        """Retorna True si el stock está bajo el mínimo"""
        return self.quantity <= self.minimum_stock

    def __repr__(self):
        return f"<Stock(id={self.id}, table={self.component_table}, qty={self.quantity})>"
