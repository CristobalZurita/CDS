"""
Modelo Warranty para gestión de garantías
=========================================
Sistema completo de garantías con claims y seguimiento.
ADITIVO: Nueva tabla, no modifica existentes.
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from enum import Enum
from app.core.database import Base


class WarrantyType(str, Enum):
    """Tipos de garantía"""
    LABOR = "labor"          # Solo mano de obra
    PARTS = "parts"          # Solo repuestos
    FULL = "full"            # Completa (mano de obra + repuestos)
    LIMITED = "limited"      # Limitada (condiciones específicas)
    EXTENDED = "extended"    # Extendida (comprada por cliente)


class WarrantyStatus(str, Enum):
    """Estados de garantía"""
    ACTIVE = "active"        # Vigente
    EXPIRED = "expired"      # Vencida
    VOIDED = "voided"        # Anulada
    CLAIMED = "claimed"      # Con reclamo en proceso
    USED = "used"            # Usada (reclamo exitoso)


class ClaimStatus(str, Enum):
    """Estados de reclamo de garantía"""
    SUBMITTED = "submitted"    # Enviado
    UNDER_REVIEW = "under_review"  # En revisión
    APPROVED = "approved"      # Aprobado
    REJECTED = "rejected"      # Rechazado
    IN_PROGRESS = "in_progress"  # En reparación
    COMPLETED = "completed"    # Completado


class Warranty(Base):
    """
    Garantía asociada a una reparación.

    Cada reparación puede tener una garantía que cubre:
    - Un período de tiempo
    - Ciertos tipos de fallas
    - Mano de obra y/o repuestos
    """
    __tablename__ = "warranties"

    id = Column(Integer, primary_key=True, index=True)

    # Referencias
    repair_id = Column(Integer, ForeignKey("repairs.id"), nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True, index=True)

    # Tipo y duración
    warranty_type = Column(String(20), default=WarrantyType.FULL.value, nullable=False)
    duration_days = Column(Integer, default=90, nullable=False)  # Duración en días

    # Fechas
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)

    # Estado
    status = Column(String(20), default=WarrantyStatus.ACTIVE.value, nullable=False, index=True)

    # Cobertura
    coverage_description = Column(Text, nullable=True)  # Qué cubre
    exclusions = Column(Text, nullable=True)  # Qué NO cubre
    max_claim_amount = Column(Integer, nullable=True)  # Monto máximo en centavos
    max_claims = Column(Integer, default=1)  # Número máximo de reclamos

    # Tracking de uso
    claims_used = Column(Integer, default=0)
    amount_claimed = Column(Integer, default=0)  # Total reclamado en centavos

    # Términos
    terms_accepted = Column(Boolean, default=False)
    terms_accepted_at = Column(DateTime, nullable=True)
    terms_version = Column(String(20), nullable=True)

    # Auditoría
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    voided_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    void_reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    repair = relationship("Repair", back_populates="warranty")
    client = relationship("Client", back_populates="warranties")
    claims = relationship("WarrantyClaim", back_populates="warranty", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Warranty(id={self.id}, repair_id={self.repair_id}, status={self.status})>"

    @property
    def is_active(self) -> bool:
        """Verifica si la garantía está vigente"""
        if self.status != WarrantyStatus.ACTIVE.value:
            return False
        now = datetime.utcnow()
        return self.start_date <= now <= self.end_date

    @property
    def days_remaining(self) -> int:
        """Días restantes de garantía"""
        if not self.is_active:
            return 0
        delta = self.end_date - datetime.utcnow()
        return max(0, delta.days)

    @property
    def can_claim(self) -> bool:
        """Verifica si se puede hacer un reclamo"""
        if not self.is_active:
            return False
        if self.claims_used >= self.max_claims:
            return False
        if self.max_claim_amount and self.amount_claimed >= self.max_claim_amount:
            return False
        return True

    @staticmethod
    def create_for_repair(repair_id: int, warranty_type: str = "full",
                          duration_days: int = 90, **kwargs) -> "Warranty":
        """Factory method para crear garantía estándar"""
        now = datetime.utcnow()
        return Warranty(
            repair_id=repair_id,
            warranty_type=warranty_type,
            duration_days=duration_days,
            start_date=now,
            end_date=now + timedelta(days=duration_days),
            **kwargs
        )


class WarrantyClaim(Base):
    """
    Reclamo de garantía.

    Registra cada vez que un cliente hace uso de su garantía.
    """
    __tablename__ = "warranty_claims"

    id = Column(Integer, primary_key=True, index=True)

    # Referencias
    warranty_id = Column(Integer, ForeignKey("warranties.id"), nullable=False, index=True)
    new_repair_id = Column(Integer, ForeignKey("repairs.id"), nullable=True)  # Nueva reparación

    # Identificación
    claim_number = Column(String(50), unique=True, nullable=False, index=True)

    # Estado
    status = Column(String(20), default=ClaimStatus.SUBMITTED.value, nullable=False, index=True)

    # Descripción del problema
    problem_description = Column(Text, nullable=False)
    fault_type = Column(String(100), nullable=True)  # Tipo de falla reportada

    # Evaluación
    is_covered = Column(Boolean, nullable=True)  # ¿Está cubierto por garantía?
    rejection_reason = Column(Text, nullable=True)
    evaluation_notes = Column(Text, nullable=True)

    # Costos
    estimated_cost = Column(Integer, default=0)  # Costo estimado
    actual_cost = Column(Integer, default=0)  # Costo real
    customer_copay = Column(Integer, default=0)  # Copago del cliente (si aplica)

    # Fechas
    submitted_at = Column(DateTime, default=datetime.utcnow)
    evaluated_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)

    # Auditoría
    submitted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    evaluated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    warranty = relationship("Warranty", back_populates="claims")
    new_repair = relationship("Repair", foreign_keys=[new_repair_id])

    def __repr__(self):
        return f"<WarrantyClaim(id={self.id}, claim_number={self.claim_number}, status={self.status})>"

    @staticmethod
    def generate_claim_number(db_session) -> str:
        """Genera número de reclamo secuencial"""
        year = datetime.utcnow().year
        last = db_session.query(WarrantyClaim).filter(
            WarrantyClaim.claim_number.like(f"WC-{year}-%")
        ).order_by(WarrantyClaim.id.desc()).first()

        if last:
            try:
                last_num = int(last.claim_number.split("-")[-1])
                next_num = last_num + 1
            except ValueError:
                next_num = 1
        else:
            next_num = 1

        return f"WC-{year}-{next_num:05d}"
