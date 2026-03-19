from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.warranty import Warranty, WarrantyClaim, WarrantyType

DEFAULT_DURATIONS = {
    WarrantyType.LABOR.value: 30,
    WarrantyType.PARTS.value: 90,
    WarrantyType.FULL.value: 90,
    WarrantyType.LIMITED.value: 30,
    WarrantyType.EXTENDED.value: 180,
}


def get_warranty_or_404(db: Session, warranty_id: int) -> Warranty:
    warranty = db.query(Warranty).filter(Warranty.id == warranty_id).first()
    if not warranty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Garantía {warranty_id} no encontrada",
        )
    return warranty


def get_claim_or_404(db: Session, claim_id: int) -> WarrantyClaim:
    claim = db.query(WarrantyClaim).filter(WarrantyClaim.id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reclamo {claim_id} no encontrado",
        )
    return claim


def default_coverage(warranty_type: str) -> str:
    coverages = {
        WarrantyType.LABOR.value: "Cubre mano de obra por defectos en el servicio realizado.",
        WarrantyType.PARTS.value: "Cubre repuestos instalados por defectos de fábrica.",
        WarrantyType.FULL.value: "Cubre mano de obra y repuestos por defectos en la reparación.",
        WarrantyType.LIMITED.value: "Cobertura limitada según condiciones específicas.",
        WarrantyType.EXTENDED.value: "Cobertura extendida de mano de obra y repuestos.",
    }
    return coverages.get(warranty_type, coverages[WarrantyType.FULL.value])


def default_exclusions() -> str:
    return """No cubre:
- Daños por mal uso o negligencia
- Daños por líquidos o humedad
- Daños físicos (golpes, caídas)
- Modificaciones no autorizadas
- Desgaste normal de componentes
- Daños por fluctuaciones eléctricas
- Problemas no relacionados con la reparación original"""
