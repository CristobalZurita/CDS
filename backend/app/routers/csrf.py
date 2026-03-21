"""
CSRF Token Endpoint
Frontend calls this to get CSRF token on page load.

Stateless signed tokens keep the current frontend contract intact while
avoiding process-local in-memory validation.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Any, Dict

from fastapi import APIRouter, Request

from app.core.config import settings

router = APIRouter(prefix="/api", tags=["csrf"])

_CSRF_TOKEN_TTL_SECONDS = 15 * 60
_CSRF_TOKEN_VERSION = 1


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(f"{value}{padding}".encode("ascii"))


def _resolve_csrf_secret() -> str:
    return (
        settings.secret_key
        or settings.jwt_secret
        or settings.jwt_refresh_secret
        or "cds-dev-csrf-secret"
    )


def _resolve_client_ip(request: Request) -> str:
    return (request.client.host if request.client and request.client.host else "unknown").strip()


def _fingerprint_client(request: Request, *, secret: str | None = None) -> str:
    base_secret = secret or _resolve_csrf_secret()
    client_ip = _resolve_client_ip(request)
    return hashlib.sha256(f"{client_ip}:{base_secret}".encode("utf-8")).hexdigest()


def _sign_payload(payload_segment: str, *, secret: str | None = None) -> str:
    base_secret = (secret or _resolve_csrf_secret()).encode("utf-8")
    signature = hmac.new(base_secret, payload_segment.encode("ascii"), hashlib.sha256).digest()
    return _b64url_encode(signature)


def _issue_csrf_token_payload(request: Request) -> Dict[str, Any]:
    now = int(time.time())
    return {
        "v": _CSRF_TOKEN_VERSION,
        "iat": now,
        "exp": now + _CSRF_TOKEN_TTL_SECONDS,
        "cip": _fingerprint_client(request),
        "nonce": secrets.token_urlsafe(12),
    }


def issue_csrf_token(request: Request) -> str:
    payload = _issue_csrf_token_payload(request)
    payload_segment = _b64url_encode(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )
    return f"{payload_segment}.{_sign_payload(payload_segment)}"


@router.get("/csrf-token")
async def get_csrf_token(request: Request) -> Dict[str, str]:
    """
    Generate and return CSRF token for frontend
    Frontend should:
    1. Call this endpoint on page load
    2. Store token in sessionStorage
    3. Include in X-CSRF-Token header for POST/PUT/DELETE requests
    """
    token = issue_csrf_token(request)

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
    
    csrf_token = (
        token or
        request.headers.get("X-CSRF-Token") or
        request.cookies.get("_csrf")
    )

    if not csrf_token:
        return False

    try:
        payload_segment, signature_segment = csrf_token.split(".", 1)
    except ValueError:
        return False

    expected_signature = _sign_payload(payload_segment)
    if not hmac.compare_digest(signature_segment, expected_signature):
        return False

    try:
        payload = json.loads(_b64url_decode(payload_segment).decode("utf-8"))
    except (ValueError, TypeError, json.JSONDecodeError):
        return False

    if payload.get("v") != _CSRF_TOKEN_VERSION:
        return False

    exp = payload.get("exp")
    if not isinstance(exp, int) or exp < int(time.time()):
        return False

    expected_fingerprint = _fingerprint_client(request)
    if payload.get("cip") != expected_fingerprint:
        return False

    return True
