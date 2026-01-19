"""
Pydantic schemas for newsletter subscriptions.
"""

from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime


class NewsletterSubscribe(BaseModel):
    email: EmailStr
    source_url: Optional[str] = None


class NewsletterSubscriptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    source_url: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
