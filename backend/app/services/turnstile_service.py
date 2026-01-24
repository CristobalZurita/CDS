"""
Cloudflare Turnstile verification service.
ADITIVO: new helper for public form validation.
"""
import json
import os
import urllib.request
import urllib.parse
from dotenv import load_dotenv


TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


def _load_env_for_dev() -> None:
    if os.getenv("ENVIRONMENT", "development").lower() in ("production", "prod"):
        return
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    repo_root = os.path.abspath(os.path.join(base_dir, ".."))
    backend_env = os.path.join(base_dir, ".env")
    root_env = os.path.join(repo_root, ".env")
    if os.path.exists(backend_env):
        load_dotenv(backend_env)
    elif os.path.exists(root_env):
        load_dotenv(root_env)


def verify_turnstile(token: str, remoteip: str | None = None) -> bool:
    if os.getenv("TURNSTILE_DISABLE", "false").lower() == "true":
        return True
    secret = os.getenv("TURNSTILE_SECRET_KEY")
    if not secret:
        _load_env_for_dev()
        secret = os.getenv("TURNSTILE_SECRET_KEY")
    if not secret:
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
