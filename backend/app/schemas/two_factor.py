"""
Schemas for 2FA flow.
"""
from pydantic import BaseModel, Field
from typing import Optional


class TwoFactorVerifyRequest(BaseModel):
    challenge_id: int
    code: str = Field(..., min_length=4, max_length=10)


class TwoFactorStatus(BaseModel):
    requires_2fa: bool
    challenge_id: Optional[int] = None
