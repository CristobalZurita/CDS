import os
from slowapi import Limiter
from slowapi.util import get_remote_address

# Configure storage URI (Redis recommended for production). Default: in-memory (not persistent)
RATE_LIMIT_STORAGE = os.getenv("RATE_LIMIT_STORAGE_URI", "memory://")

limiter = Limiter(key_func=get_remote_address, storage_uri=RATE_LIMIT_STORAGE)


def get_limiter():
    return limiter
