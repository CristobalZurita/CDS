"""Stats endpoints (API v1)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.client import Client
from app.models.repair import Repair
from app.models.inventory import Product

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/")
def get_stats(db: Session = Depends(get_db)):
    return {
        "users": db.query(User).count(),
        "clients": db.query(Client).count(),
        "repairs": db.query(Repair).count(),
        "products": db.query(Product).count()
    }
