from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.warranty import ClaimStatus, WarrantyClaim, WarrantyStatus
from app.services.warranty_support import get_claim_or_404, get_warranty_or_404


class WarrantyClaimService:
    def __init__(self, db: Session):
        self.db = db

    def submit_claim(
        self,
        warranty_id: int,
        problem_description: str,
        fault_type: Optional[str] = None,
        submitted_by: Optional[int] = None,
    ) -> WarrantyClaim:
        warranty = get_warranty_or_404(self.db, warranty_id)

        if not warranty.can_claim:
            if not warranty.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La garantía no está vigente",
                )
            if warranty.claims_used >= warranty.max_claims:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Se ha alcanzado el máximo de reclamos permitidos",
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede presentar reclamo",
            )

        claim = WarrantyClaim(
            warranty_id=warranty_id,
            claim_number=WarrantyClaim.generate_claim_number(self.db),
            status=ClaimStatus.SUBMITTED.value,
            problem_description=problem_description,
            fault_type=fault_type,
            submitted_by=submitted_by,
            submitted_at=datetime.utcnow(),
        )
        self.db.add(claim)
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
        evaluated_by: Optional[int] = None,
    ) -> WarrantyClaim:
        claim = get_claim_or_404(self.db, claim_id)
        if claim.status != ClaimStatus.SUBMITTED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El reclamo ya fue evaluado",
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
            claim.warranty.status = WarrantyStatus.ACTIVE.value

        self.db.commit()
        self.db.refresh(claim)
        return claim

    def process_claim(
        self,
        claim_id: int,
        new_repair_id: Optional[int] = None,
        actual_cost: int = 0,
        customer_copay: int = 0,
    ) -> WarrantyClaim:
        claim = get_claim_or_404(self.db, claim_id)
        if claim.status != ClaimStatus.APPROVED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se pueden procesar reclamos aprobados",
            )

        claim.status = ClaimStatus.IN_PROGRESS.value
        claim.new_repair_id = new_repair_id
        claim.actual_cost = actual_cost
        claim.customer_copay = customer_copay
        self.db.commit()
        self.db.refresh(claim)
        return claim

    def complete_claim(self, claim_id: int) -> WarrantyClaim:
        claim = get_claim_or_404(self.db, claim_id)
        if claim.status != ClaimStatus.IN_PROGRESS.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se pueden completar reclamos en proceso",
            )

        claim.status = ClaimStatus.COMPLETED.value
        claim.resolved_at = datetime.utcnow()
        warranty = claim.warranty
        warranty.claims_used += 1
        warranty.amount_claimed += claim.actual_cost
        warranty.status = WarrantyStatus.USED.value
        self.db.commit()
        self.db.refresh(claim)
        return claim
