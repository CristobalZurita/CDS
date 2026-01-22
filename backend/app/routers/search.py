"""
Router de búsqueda global (Admin)
=================================
Busca clientes, instrumentos, OT y productos desde un solo endpoint.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import require_permission
from app.models.client import Client
from app.models.device import Device
from app.models.repair import Repair
from app.models.inventory import Product
from app.models.ticket import Ticket
from app.models.manual_document import ManualDocument
from app.models.purchase_request import PurchaseRequest

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/")
def search_all(
    query: str = Query(..., min_length=2, description="Texto de búsqueda"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("clients", "read"))
):
    q = f"%{query.strip()}%"
    results = []

    clients = db.query(Client).filter(
        (Client.name.ilike(q)) |
        (Client.email.ilike(q)) |
        (Client.phone.ilike(q)) |
        (Client.address.ilike(q))
    ).limit(limit).all()
    for client in clients:
        results.append({
            "type": "client",
            "id": client.id,
            "label": client.name,
            "subtitle": client.email,
            "client_id": client.id
        })

    devices = db.query(Device).filter(
        (Device.model.ilike(q)) |
        (Device.serial_number.ilike(q)) |
        (Device.brand_other.ilike(q))
    ).limit(limit).all()
    for device in devices:
        results.append({
            "type": "device",
            "id": device.id,
            "label": device.model,
            "subtitle": device.serial_number,
            "client_id": device.client_id
        })

    repairs = db.query(Repair).filter(
        (Repair.repair_number.ilike(q)) |
        (Repair.problem_reported.ilike(q))
    ).limit(limit).all()
    for repair in repairs:
        results.append({
            "type": "repair",
            "id": repair.id,
            "label": repair.repair_number,
            "subtitle": repair.problem_reported,
            "repair_id": repair.id
        })

    products = db.query(Product).filter(
        (Product.name.ilike(q)) |
        (Product.sku.ilike(q))
    ).limit(limit).all()
    for product in products:
        results.append({
            "type": "inventory",
            "id": product.id,
            "label": product.name,
            "subtitle": product.sku,
            "product_id": product.id
        })

    tickets = db.query(Ticket).filter(
        (Ticket.subject.ilike(q))
    ).limit(limit).all()
    for ticket in tickets:
        results.append({
            "type": "ticket",
            "id": ticket.id,
            "label": ticket.subject,
            "subtitle": ticket.status,
            "ticket_id": ticket.id
        })

    manuals = db.query(ManualDocument).filter(
        (ManualDocument.title.ilike(q))
    ).limit(limit).all()
    for manual in manuals:
        results.append({
            "type": "manual",
            "id": manual.id,
            "label": manual.title,
            "subtitle": manual.source,
            "manual_id": manual.id
        })

    purchase_requests = db.query(PurchaseRequest).filter(
        (PurchaseRequest.notes.ilike(q))
    ).limit(limit).all()
    for req in purchase_requests:
        results.append({
            "type": "purchase_request",
            "id": req.id,
            "label": f"PR-{req.id}",
            "subtitle": req.status,
            "purchase_request_id": req.id
        })

    return results[:limit]
