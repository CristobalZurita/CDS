"""
WarrantyService - fachada estable para garantías y reclamos.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.repair import Repair
from app.models.warranty import (
    Warranty,
    WarrantyClaim,
    WarrantyStatus,
    WarrantyType,
)
from app.services.warranty_claim_service import WarrantyClaimService
from app.services.warranty_support import (
    DEFAULT_DURATIONS,
    default_coverage,
    default_exclusions,
    get_claim_or_404,
    get_warranty_or_404,
)


class WarrantyService:
    DEFAULT_DURATIONS = DEFAULT_DURATIONS

    def __init__(self, db: Session):
        self.db = db
        self.claim_service = WarrantyClaimService(db)

    def create_warranty(
        self,
        repair_id: int,
        warranty_type: str = WarrantyType.FULL.value,
        duration_days: Optional[int] = None,
        coverage_description: Optional[str] = None,
        exclusions: Optional[str] = None,
        max_claim_amount: Optional[int] = None,
        max_claims: int = 1,
        created_by: Optional[int] = None,
    ) -> Warranty:
        repair = self.db.query(Repair).filter(Repair.id == repair_id).first()
        if not repair:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reparación {repair_id} no encontrada",
            )

        existing = (
            self.db.query(Warranty)
            .filter(
                Warranty.repair_id == repair_id,
                Warranty.status != WarrantyStatus.VOIDED.value,
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La reparación ya tiene una garantía activa",
            )

        resolved_duration = duration_days
        if resolved_duration is None:
            resolved_duration = self.DEFAULT_DURATIONS.get(warranty_type, 90)

        client_id = None
        if hasattr(repair, "instrument") and repair.instrument and hasattr(repair.instrument, "client_id"):
            client_id = repair.instrument.client_id

        now = datetime.utcnow()
        warranty = Warranty(
            repair_id=repair_id,
            client_id=client_id,
            warranty_type=warranty_type,
            duration_days=resolved_duration,
            start_date=now,
            end_date=now + timedelta(days=resolved_duration),
            status=WarrantyStatus.ACTIVE.value,
            coverage_description=coverage_description or default_coverage(warranty_type),
            exclusions=exclusions or default_exclusions(),
            max_claim_amount=max_claim_amount,
            max_claims=max_claims,
            created_by=created_by,
        )

        self.db.add(warranty)
        self.db.commit()
        self.db.refresh(warranty)
        return warranty

    def create_for_completed_repair(
        self,
        repair_id: int,
        created_by: Optional[int] = None,
    ) -> Warranty:
        repair = self.db.query(Repair).filter(Repair.id == repair_id).first()
        if not repair:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reparación {repair_id} no encontrada",
            )

        warranty_type = WarrantyType.FULL.value
        if repair.labor_cost and not repair.parts_cost:
            warranty_type = WarrantyType.LABOR.value
        elif repair.parts_cost and not repair.labor_cost:
            warranty_type = WarrantyType.PARTS.value

        return self.create_warranty(
            repair_id=repair_id,
            warranty_type=warranty_type,
            created_by=created_by,
        )

    def submit_claim(
        self,
        warranty_id: int,
        problem_description: str,
        fault_type: Optional[str] = None,
        submitted_by: Optional[int] = None,
    ) -> WarrantyClaim:
        return self.claim_service.submit_claim(
            warranty_id=warranty_id,
            problem_description=problem_description,
            fault_type=fault_type,
            submitted_by=submitted_by,
        )

    def evaluate_claim(
        self,
        claim_id: int,
        is_covered: bool,
        evaluation_notes: Optional[str] = None,
        rejection_reason: Optional[str] = None,
        estimated_cost: int = 0,
        evaluated_by: Optional[int] = None,
    ) -> WarrantyClaim:
        return self.claim_service.evaluate_claim(
            claim_id=claim_id,
            is_covered=is_covered,
            evaluation_notes=evaluation_notes,
            rejection_reason=rejection_reason,
            estimated_cost=estimated_cost,
            evaluated_by=evaluated_by,
        )

    def process_claim(
        self,
        claim_id: int,
        new_repair_id: Optional[int] = None,
        actual_cost: int = 0,
        customer_copay: int = 0,
    ) -> WarrantyClaim:
        return self.claim_service.process_claim(
            claim_id=claim_id,
            new_repair_id=new_repair_id,
            actual_cost=actual_cost,
            customer_copay=customer_copay,
        )

    def complete_claim(self, claim_id: int) -> WarrantyClaim:
        return self.claim_service.complete_claim(claim_id)

    def void_warranty(
        self,
        warranty_id: int,
        reason: str,
        voided_by: Optional[int] = None,
    ) -> Warranty:
        warranty = get_warranty_or_404(self.db, warranty_id)
        if warranty.status == WarrantyStatus.VOIDED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La garantía ya está anulada",
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
        problem_description: Optional[str] = None,
    ) -> Dict[str, Any]:
        warranty = (
            self.db.query(Warranty)
            .filter(
                Warranty.repair_id == repair_id,
                Warranty.status != WarrantyStatus.VOIDED.value,
            )
            .first()
        )
        if not warranty:
            return {
                "has_warranty": False,
                "is_covered": False,
                "message": "No se encontró garantía para esta reparación",
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
            "exclusions": warranty.exclusions,
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
        return get_warranty_or_404(self.db, warranty_id)

    def get_claim(self, claim_id: int) -> WarrantyClaim:
        return get_claim_or_404(self.db, claim_id)

    def get_warranty_by_repair(self, repair_id: int) -> Optional[Warranty]:
        return (
            self.db.query(Warranty)
            .filter(
                Warranty.repair_id == repair_id,
                Warranty.status != WarrantyStatus.VOIDED.value,
            )
            .first()
        )

    def list_warranties(
        self,
        client_id: Optional[int] = None,
        status: Optional[str] = None,
        expiring_in_days: Optional[int] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Warranty]:
        query = self.db.query(Warranty)

        if client_id:
            query = query.filter(Warranty.client_id == client_id)
        if status:
            query = query.filter(Warranty.status == status)
        if expiring_in_days:
            expiry_date = datetime.utcnow() + timedelta(days=expiring_in_days)
            query = query.filter(
                Warranty.status == WarrantyStatus.ACTIVE.value,
                Warranty.end_date <= expiry_date,
            )

        return query.order_by(Warranty.end_date.desc()).offset(offset).limit(limit).all()

    def list_claims(
        self,
        warranty_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[WarrantyClaim]:
        query = self.db.query(WarrantyClaim)
        if warranty_id:
            query = query.filter(WarrantyClaim.warranty_id == warranty_id)
        if status:
            query = query.filter(WarrantyClaim.status == status)
        return query.order_by(WarrantyClaim.submitted_at.desc()).offset(offset).limit(limit).all()

    def update_expired_warranties(self) -> int:
        now = datetime.utcnow()
        expired = (
            self.db.query(Warranty)
            .filter(
                Warranty.status == WarrantyStatus.ACTIVE.value,
                Warranty.end_date < now,
            )
            .all()
        )

        count = 0
        for warranty in expired:
            warranty.status = WarrantyStatus.EXPIRED.value
            count += 1

        self.db.commit()
        return count

    def get_expiring_soon(self, days: int = 7) -> List[Warranty]:
        expiry_date = datetime.utcnow() + timedelta(days=days)
        return (
            self.db.query(Warranty)
            .filter(
                Warranty.status == WarrantyStatus.ACTIVE.value,
                Warranty.end_date <= expiry_date,
                Warranty.end_date > datetime.utcnow(),
            )
            .all()
        )
