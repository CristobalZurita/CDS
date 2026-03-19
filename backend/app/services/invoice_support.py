from __future__ import annotations

from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.invoice import Invoice, InvoiceSequence, InvoiceType
from app.models.repair import Repair


def get_invoice_or_404(db: Session, invoice_id: int) -> Invoice:
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Factura {invoice_id} no encontrada",
        )
    return invoice


def get_repair_or_404(db: Session, repair_id: int) -> Repair:
    repair = db.query(Repair).filter(Repair.id == repair_id).first()
    if not repair:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reparación {repair_id} no encontrada",
        )
    return repair


def resolve_invoice_prefix(invoice_type: str) -> str:
    prefix_map = {
        InvoiceType.INVOICE.value: "F",
        InvoiceType.QUOTE.value: "Q",
        InvoiceType.CREDIT_NOTE.value: "NC",
        InvoiceType.RECEIPT.value: "R",
    }
    return prefix_map.get(invoice_type, "F")


def generate_invoice_number(db: Session, prefix: str) -> str:
    year = datetime.utcnow().year
    sequence = (
        db.query(InvoiceSequence)
        .filter(
            InvoiceSequence.prefix == prefix,
            InvoiceSequence.year == year,
        )
        .with_for_update()
        .first()
    )

    if sequence:
        sequence.last_number += 1
        next_num = sequence.last_number
    else:
        sequence = InvoiceSequence(prefix=prefix, year=year, last_number=1)
        db.add(sequence)
        next_num = 1

    db.flush()
    return f"{prefix}-{year}-{next_num:05d}"


def resolve_client_snapshot(db: Session, client_id: int | None) -> dict:
    client_name = client_email = client_phone = client_address = client_tax_id = None
    if client_id:
        client = db.query(Client).filter(Client.id == client_id).first()
        if client:
            client_name = client.name
            client_email = client.email
            client_phone = client.phone
            client_address = client.address
            client_tax_id = getattr(client, "tax_id", None)

    return {
        "client_name": client_name,
        "client_email": client_email,
        "client_phone": client_phone,
        "client_address": client_address,
        "client_tax_id": client_tax_id,
    }
