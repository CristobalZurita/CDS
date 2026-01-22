from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.dependencies import require_permission, get_current_user
from app.models.ticket import Ticket, TicketMessage
from app.schemas.ticket import TicketCreate, TicketOut, TicketMessageCreate, TicketMessageOut

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("/", response_model=List[TicketOut])
def list_tickets(
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("tickets", "read")),
):
    tickets = db.query(Ticket).order_by(Ticket.updated_at.desc()).all()
    return tickets


@router.post("/", response_model=TicketOut, status_code=201)
def create_ticket(
    payload: TicketCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    ticket = Ticket(
        client_id=payload.client_id,
        repair_id=payload.repair_id,
        created_by=int(user.get("user_id")) if user else None,
        subject=payload.subject.strip(),
        priority=payload.priority or "normal",
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    msg = TicketMessage(
        ticket_id=ticket.id,
        author_id=ticket.created_by,
        body=payload.message.strip(),
    )
    db.add(msg)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.get("/{ticket_id}", response_model=TicketOut)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("tickets", "read")),
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.post("/{ticket_id}/messages", response_model=TicketMessageOut, status_code=201)
def add_ticket_message(
    ticket_id: int,
    payload: TicketMessageCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    msg = TicketMessage(
        ticket_id=ticket_id,
        author_id=int(user.get("user_id")) if user else None,
        body=payload.message.strip(),
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


@router.patch("/{ticket_id}")
def update_ticket_status(
    ticket_id: int,
    status: str,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("tickets", "update")),
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    ticket.status = status
    db.commit()
    return {"ok": True}
