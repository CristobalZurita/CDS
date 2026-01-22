"""
Cloudflare Turnstile verification service.
ADITIVO: new helper for public form validation.
"""
import json
import os
import urllib.request
import urllib.parse


TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


def verify_turnstile(token: str, remoteip: str | None = None) -> bool:
    secret = os.getenv("TURNSTILE_SECRET_KEY")
    if not secret:
        # If secret is missing, treat as failure in production
        return False

    data = {
        "secret": secret,
        "response": token,
    }
    if remoteip:
        data["remoteip"] = remoteip

    encoded = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(TURNSTILE_VERIFY_URL, data=encoded, method="POST")
    with urllib.request.urlopen(req, timeout=5) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    return bool(payload.get("success"))
