"""
WarrantyService - Servicio de Garantías
=======================================
Gestiona garantías, reclamos y cobertura.
ADITIVO: Nuevo servicio, no modifica existentes.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from app.models.warranty import (
    Warranty, WarrantyClaim, WarrantyType, WarrantyStatus, ClaimStatus
)
from app.models.repair import Repair
from app.models.client import Client


class WarrantyService:
    """Servicio para gestión de garantías"""

    # Configuración de garantías por defecto
    DEFAULT_DURATIONS = {
        WarrantyType.LABOR.value: 30,      # 30 días solo mano de obra
        WarrantyType.PARTS.value: 90,      # 90 días solo repuestos
        WarrantyType.FULL.value: 90,       # 90 días completa
        WarrantyType.LIMITED.value: 30,    # 30 días limitada
        WarrantyType.EXTENDED.value: 180   # 180 días extendida
    }

    def __init__(self, db: Session):
        self.db = db

    def create_warranty(
        self,
        repair_id: int,
        warranty_type: str = WarrantyType.FULL.value,
        duration_days: Optional[int] = None,
        coverage_description: Optional[str] = None,
        exclusions: Optional[str] = None,
        max_claim_amount: Optional[int] = None,
        max_claims: int = 1,
        created_by: Optional[int] = None
    ) -> Warranty:
        """
        Crea una garantía para una reparación.

        Args:
            repair_id: ID de la reparación
            warranty_type: Tipo de garantía
            duration_days: Duración en días (usa default si None)
            coverage_description: Descripción de cobertura
            exclusions: Exclusiones
            max_claim_amount: Monto máximo de reclamo
            max_claims: Número máximo de reclamos
            created_by: Usuario que crea

        Returns:
            Warranty creada
        """
        # Verificar que la reparación existe
        repair = self.db.query(Repair).filter(Repair.id == repair_id).first()
        if not repair:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reparación {repair_id} no encontrada"
            )

        # Verificar que no tenga ya garantía activa
        existing = self.db.query(Warranty).filter(
            Warranty.repair_id == repair_id,
            Warranty.status != WarrantyStatus.VOIDED.value
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La reparación ya tiene una garantía activa"
            )

        # Usar duración por defecto si no se especifica
        if duration_days is None:
            duration_days = self.DEFAULT_DURATIONS.get(warranty_type, 90)

        # Obtener client_id desde repair
        client_id = None
        if hasattr(repair, 'instrument') and repair.instrument:
            if hasattr(repair.instrument, 'client_id'):
                client_id = repair.instrument.client_id

        # Crear garantía
        now = datetime.utcnow()
        warranty = Warranty(
            repair_id=repair_id,
            client_id=client_id,
            warranty_type=warranty_type,
            duration_days=duration_days,
            start_date=now,
            end_date=now + timedelta(days=duration_days),
            status=WarrantyStatus.ACTIVE.value,
            coverage_description=coverage_description or self._default_coverage(warranty_type),
            exclusions=exclusions or self._default_exclusions(),
            max_claim_amount=max_claim_amount,
            max_claims=max_claims,
            created_by=created_by
        )

        self.db.add(warranty)
        self.db.commit()
        self.db.refresh(warranty)

        return warranty

    def create_for_completed_repair(
        self,
        repair_id: int,
        created_by: Optional[int] = None
    ) -> Warranty:
        """
        Crea garantía automáticamente cuando una reparación se completa.

        Args:
            repair_id: ID de la reparación
            created_by: Usuario que crea

        Returns:
            Warranty creada
        """
        repair = self.db.query(Repair).filter(Repair.id == repair_id).first()
        if not repair:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reparación {repair_id} no encontrada"
            )

        # Determinar tipo de garantía basado en la reparación
        warranty_type = WarrantyType.FULL.value
        if repair.labor_cost and not repair.parts_cost:
            warranty_type = WarrantyType.LABOR.value
        elif repair.parts_cost and not repair.labor_cost:
            warranty_type = WarrantyType.PARTS.value

        return self.create_warranty(
            repair_id=repair_id,
            warranty_type=warranty_type,
            created_by=created_by
        )

    def submit_claim(
        self,
        warranty_id: int,
        problem_description: str,
        fault_type: Optional[str] = None,
        submitted_by: Optional[int] = None
    ) -> WarrantyClaim:
        """
        Presenta un reclamo de garantía.

        Args:
            warranty_id: ID de la garantía
            problem_description: Descripción del problema
            fault_type: Tipo de falla
            submitted_by: Usuario que presenta

        Returns:
            WarrantyClaim creado
        """
        warranty = self.get_warranty(warranty_id)

        # Verificar que se puede reclamar
        if not warranty.can_claim:
            if not warranty.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La garantía no está vigente"
                )
            if warranty.claims_used >= warranty.max_claims:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Se ha alcanzado el máximo de reclamos permitidos"
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede presentar reclamo"
            )

        # Generar número de reclamo
        claim_number = WarrantyClaim.generate_claim_number(self.db)

        # Crear reclamo
        claim = WarrantyClaim(
            warranty_id=warranty_id,
            claim_number=claim_number,
            status=ClaimStatus.SUBMITTED.value,
            problem_description=problem_description,
            fault_type=fault_type,
            submitted_by=submitted_by,
            submitted_at=datetime.utcnow()
        )

        self.db.add(claim)

        # Actualizar estado de garantía
        warranty.status = WarrantyStatus.CLAIMED.value

        self.db.commit()
        self.db.refresh(claim)

        return claim

    def evaluate_claim(
        self,
        claim_id: int,
        is_covered: bool,
        evaluation_notes: Optional[str] = None,
        rejection_reason: Optional[str] = None,
        estimated_cost: int = 0,
        evaluated_by: Optional[int] = None
    ) -> WarrantyClaim:
        """
        Evalúa un reclamo de garantía.

        Args:
            claim_id: ID del reclamo
            is_covered: ¿Está cubierto?
            evaluation_notes: Notas de evaluación
            rejection_reason: Razón de rechazo (si aplica)
            estimated_cost: Costo estimado
            evaluated_by: Usuario evaluador

        Returns:
            WarrantyClaim actualizado
        """
        claim = self.get_claim(claim_id)

        if claim.status != ClaimStatus.SUBMITTED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El reclamo ya fue evaluado"
            )

        claim.is_covered = is_covered
        claim.evaluation_notes = evaluation_notes
        claim.estimated_cost = estimated_cost
        claim.evaluated_by = evaluated_by
        claim.evaluated_at = datetime.utcnow()

        if is_covered:
            claim.status = ClaimStatus.APPROVED.value
        else:
            claim.status = ClaimStatus.REJECTED.value
            claim.rejection_reason = rejection_reason

            # Restaurar estado de garantía si se rechaza
            claim.warranty.status = WarrantyStatus.ACTIVE.value

        self.db.commit()
        self.db.refresh(claim)

        return claim

    def process_claim(
        self,
        claim_id: int,
        new_repair_id: Optional[int] = None,
        actual_cost: int = 0,
        customer_copay: int = 0
    ) -> WarrantyClaim:
        """
        Procesa un reclamo aprobado (inicia reparación).

        Args:
            claim_id: ID del reclamo
            new_repair_id: ID de nueva reparación
            actual_cost: Costo real
            customer_copay: Copago del cliente

        Returns:
            WarrantyClaim actualizado
        """
        claim = self.get_claim(claim_id)

        if claim.status != ClaimStatus.APPROVED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se pueden procesar reclamos aprobados"
            )

        claim.status = ClaimStatus.IN_PROGRESS.value
        claim.new_repair_id = new_repair_id
        claim.actual_cost = actual_cost
        claim.customer_copay = customer_copay

        self.db.commit()
        self.db.refresh(claim)

        return claim

    def complete_claim(self, claim_id: int) -> WarrantyClaim:
        """
        Completa un reclamo (reparación finalizada).

        Args:
            claim_id: ID del reclamo

        Returns:
            WarrantyClaim completado
        """
        claim = self.get_claim(claim_id)

        if claim.status != ClaimStatus.IN_PROGRESS.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se pueden completar reclamos en proceso"
            )

        claim.status = ClaimStatus.COMPLETED.value
        claim.resolved_at = datetime.utcnow()

        # Actualizar warranty
        warranty = claim.warranty
        warranty.claims_used += 1
        warranty.amount_claimed += claim.actual_cost
        warranty.status = WarrantyStatus.USED.value

        self.db.commit()
        self.db.refresh(claim)

        return claim

    def void_warranty(
        self,
        warranty_id: int,
        reason: str,
        voided_by: Optional[int] = None
    ) -> Warranty:
        """
        Anula una garantía.

        Args:
            warranty_id: ID de la garantía
            reason: Razón de anulación
            voided_by: Usuario que anula

        Returns:
            Warranty anulada
        """
        warranty = self.get_warranty(warranty_id)

        if warranty.status == WarrantyStatus.VOIDED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La garantía ya está anulada"
            )

        warranty.status = WarrantyStatus.VOIDED.value
        warranty.voided_by = voided_by
        warranty.void_reason = reason

        self.db.commit()
        self.db.refresh(warranty)

        return warranty

    def check_coverage(
        self,
        repair_id: int,
        problem_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verifica cobertura de garantía para una reparación.

        Args:
            repair_id: ID de la reparación original
            problem_description: Descripción del nuevo problema

        Returns:
            Diccionario con estado de cobertura
        """
        warranty = self.db.query(Warranty).filter(
            Warranty.repair_id == repair_id,
            Warranty.status != WarrantyStatus.VOIDED.value
        ).first()

        if not warranty:
            return {
                "has_warranty": False,
                "is_covered": False,
                "message": "No se encontró garantía para esta reparación"
            }

        result = {
            "has_warranty": True,
            "warranty_id": warranty.id,
            "warranty_type": warranty.warranty_type,
            "start_date": warranty.start_date.isoformat(),
            "end_date": warranty.end_date.isoformat(),
            "days_remaining": warranty.days_remaining,
            "claims_used": warranty.claims_used,
            "max_claims": warranty.max_claims,
            "can_claim": warranty.can_claim,
            "coverage": warranty.coverage_description,
            "exclusions": warranty.exclusions
        }

        if warranty.is_active:
            result["is_covered"] = True
            result["message"] = f"Garantía vigente. Quedan {warranty.days_remaining} días."
        else:
            result["is_covered"] = False
            result["message"] = "La garantía ha expirado"
            result["status"] = warranty.status

        return result

    def get_warranty(self, warranty_id: int) -> Warranty:
        """Obtiene una garantía por ID"""
        warranty = self.db.query(Warranty).filter(Warranty.id == warranty_id).first()
        if not warranty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Garantía {warranty_id} no encontrada"
            )
        return warranty

    def get_claim(self, claim_id: int) -> WarrantyClaim:
        """Obtiene un reclamo por ID"""
        claim = self.db.query(WarrantyClaim).filter(WarrantyClaim.id == claim_id).first()
        if not claim:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reclamo {claim_id} no encontrado"
            )
        return claim

    def get_warranty_by_repair(self, repair_id: int) -> Optional[Warranty]:
        """Obtiene garantía activa de una reparación"""
        return self.db.query(Warranty).filter(
            Warranty.repair_id == repair_id,
            Warranty.status != WarrantyStatus.VOIDED.value
        ).first()

    def list_warranties(
        self,
        client_id: Optional[int] = None,
        status: Optional[str] = None,
        expiring_in_days: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Warranty]:
        """Lista garantías con filtros"""
        query = self.db.query(Warranty)

        if client_id:
            query = query.filter(Warranty.client_id == client_id)
        if status:
            query = query.filter(Warranty.status == status)
        if expiring_in_days:
            expiry_date = datetime.utcnow() + timedelta(days=expiring_in_days)
            query = query.filter(
                Warranty.status == WarrantyStatus.ACTIVE.value,
                Warranty.end_date <= expiry_date
            )

        return query.order_by(Warranty.end_date.desc()).offset(offset).limit(limit).all()

    def list_claims(
        self,
        warranty_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[WarrantyClaim]:
        """Lista reclamos con filtros"""
        query = self.db.query(WarrantyClaim)

        if warranty_id:
            query = query.filter(WarrantyClaim.warranty_id == warranty_id)
        if status:
            query = query.filter(WarrantyClaim.status == status)

        return query.order_by(WarrantyClaim.submitted_at.desc()).offset(offset).limit(limit).all()

    def update_expired_warranties(self) -> int:
        """Marca como expiradas las garantías vencidas"""
        now = datetime.utcnow()
        expired = self.db.query(Warranty).filter(
            Warranty.status == WarrantyStatus.ACTIVE.value,
            Warranty.end_date < now
        ).all()

        count = 0
        for warranty in expired:
            warranty.status = WarrantyStatus.EXPIRED.value
            count += 1

        self.db.commit()
        return count

    def get_expiring_soon(self, days: int = 7) -> List[Warranty]:
        """Obtiene garantías que expiran pronto"""
        expiry_date = datetime.utcnow() + timedelta(days=days)
        return self.db.query(Warranty).filter(
            Warranty.status == WarrantyStatus.ACTIVE.value,
            Warranty.end_date <= expiry_date,
            Warranty.end_date > datetime.utcnow()
        ).all()

    def _default_coverage(self, warranty_type: str) -> str:
        """Descripción de cobertura por defecto"""
        coverages = {
            WarrantyType.LABOR.value: "Cubre mano de obra por defectos en el servicio realizado.",
            WarrantyType.PARTS.value: "Cubre repuestos instalados por defectos de fábrica.",
            WarrantyType.FULL.value: "Cubre mano de obra y repuestos por defectos en la reparación.",
            WarrantyType.LIMITED.value: "Cobertura limitada según condiciones específicas.",
            WarrantyType.EXTENDED.value: "Cobertura extendida de mano de obra y repuestos."
        }
        return coverages.get(warranty_type, coverages[WarrantyType.FULL.value])

    def _default_exclusions(self) -> str:
        """Exclusiones por defecto"""
        return """No cubre:
- Daños por mal uso o negligencia
- Daños por líquidos o humedad
- Daños físicos (golpes, caídas)
- Modificaciones no autorizadas
- Desgaste normal de componentes
- Daños por fluctuaciones eléctricas
- Problemas no relacionados con la reparación original"""
