from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.models.newsletter_subscription import NewsletterSubscription
from app.schemas.newsletter import NewsletterSubscribe, NewsletterSubscriptionOut

router = APIRouter(prefix="/newsletter", tags=["Newsletter"])


@router.post("/subscribe", status_code=201)
def subscribe(payload: NewsletterSubscribe, request: Request, db: Session = Depends(get_db)):
    existing = db.query(NewsletterSubscription).filter(NewsletterSubscription.email == payload.email).first()
    if existing:
        existing.is_active = True
        existing.source_url = payload.source_url or existing.source_url
        existing.ip_address = request.client.host if request.client else existing.ip_address
        existing.user_agent = request.headers.get("user-agent") or existing.user_agent
        db.commit()
        return {"ok": True, "subscription_id": existing.id}

    subscription = NewsletterSubscription(
        email=payload.email,
        source_url=payload.source_url,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        is_active=True,
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return {"ok": True, "subscription_id": subscription.id}


@router.get("/subscriptions", response_model=List[NewsletterSubscriptionOut])
def list_subscriptions(
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    return db.query(NewsletterSubscription).order_by(NewsletterSubscription.created_at.desc()).all()
