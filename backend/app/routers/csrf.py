"""
CSRF Token Endpoint
Frontend calls this to get CSRF token on page load
"""

from fastapi import APIRouter, Request
from typing import Dict
import secrets

router = APIRouter(prefix="/api", tags=["csrf"])

# In-memory CSRF tokens (in production, use Redis or database)
csrf_tokens: Dict[str, str] = {}


@router.get("/csrf-token")
async def get_csrf_token(request: Request) -> Dict[str, str]:
    """
    Generate and return CSRF token for frontend
    Frontend should:
    1. Call this endpoint on page load
    2. Store token in sessionStorage
    3. Include in X-CSRF-Token header for POST/PUT/DELETE requests
    """
    
    # Generate token
    token = secrets.token_urlsafe(32)
    
    # Store with client IP (for validation later)
    client_ip = request.client.host
    csrf_tokens[token] = client_ip
    
    return {
        "token": token,
        "headerName": "X-CSRF-Token",
        "cookieName": "_csrf"  # For compatibility
    }


def validate_csrf_token(request: Request, token: str | None = None) -> bool:
    """
    Validate CSRF token from request
    Token can be in:
    1. X-CSRF-Token header
    2. _csrf cookie
    3. Request body (_csrf field)
    """
    
    # Get token from various sources
    csrf_token = (
        token or
        request.headers.get("X-CSRF-Token") or
        request.cookies.get("_csrf")
    )
    
    if not csrf_token:
        return False
    
    # Verify token exists and IP matches
    if csrf_token in csrf_tokens:
        stored_ip = csrf_tokens[csrf_token]
        request_ip = request.client.host
        
        # IP should match
        if stored_ip == request_ip:
            # Token is valid, remove it (one-time use)
            del csrf_tokens[csrf_token]
            return True
    
    return False
