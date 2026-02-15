"""
PHASE 3: Rate Limiting Middleware
Prevent brute force attacks and API abuse
"""

from fastapi import Request, HTTPException, status
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class RateLimitConfig:
    """Configuration for rate limiting rules"""
    
    # (max_requests, window_seconds, key_type)
    RULES = {
        # Authentication endpoints - strict
        "POST /api/auth/login": (5, 60, "ip"),  # 5 per minute
        "POST /api/auth/register": (3, 3600, "ip"),  # 3 per hour
        "POST /api/auth/refresh": (10, 60, "user"),  # 10 per minute
        "POST /api/auth/verify-2fa": (10, 60, "user"),  # 10 per minute
        
        # API endpoints - moderate
        "GET /api/repairs": (100, 60, "user"),  # 100 per minute
        "POST /api/repairs": (20, 60, "user"),  # 20 per minute
        "PUT /api/repairs/*": (20, 60, "user"),  # 20 per minute
        
        # Search endpoints - moderate
        "GET /api/search": (30, 60, "user"),  # 30 per minute
        "GET /api/categories": (50, 60, "user"),  # 50 per minute
        
        # Admin endpoints - stricter
        "DELETE /api/repairs/*": (5, 3600, "user"),  # 5 per hour
        "DELETE /api/users/*": (3, 3600, "admin"),  # 3 per hour
        
        # File uploads - strict
        "POST /api/files/upload": (10, 3600, "user"),  # 10 per hour
    }


class RateLimiter:
    """Rate limiter that tracks requests per IP/user"""
    
    def __init__(self):
        # {key: [(timestamp, endpoint), ...]}
        self.requests: Dict[str, List[Tuple[datetime, str]]] = defaultdict(list)
        # {key: (locked_until, reason)}
        self.blocked: Dict[str, Tuple[datetime, str]] = {}
    
    def _get_key(self, request: Request, key_type: str) -> str:
        """Generate key for rate limiting (IP or user ID)"""
        if key_type == "user" and hasattr(request.state, "user_id"):
            return f"user_{request.state.user_id}"
        return f"ip_{request.client.host}"
    
    def _get_rule(self, path: str, method: str) -> Optional[Tuple[int, int, str]]:
        """Get rate limit rule for endpoint"""
        endpoint = f"{method} {path}"
        
        # Exact match
        if endpoint in RateLimitConfig.RULES:
            return RateLimitConfig.RULES[endpoint]
        
        # Pattern match (for paths with IDs)
        for rule_key, rule_value in RateLimitConfig.RULES.items():
            if "*" in rule_key:
                # Convert pattern to regex
                pattern = rule_key.replace("*", ".*")
                import re
                if re.match(f"^{pattern}$", endpoint):
                    return rule_value
        
        return None
    
    async def check_rate_limit(self, request: Request) -> bool:
        """Check if request should be rate limited"""
        
        path = request.url.path
        method = request.method
        rule = self._get_rule(path, method)
        
        # No rule = no limit
        if not rule:
            return True
        
        max_requests, window_seconds, key_type = rule
        key = self._get_key(request, key_type)
        
        # Check if key is blocked
        if key in self.blocked:
            blocked_until, reason = self.blocked[key]
            if datetime.utcnow() < blocked_until:
                logger.warning(f"Request from {key} blocked: {reason}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded: {reason}. Try again later.",
                    headers={"Retry-After": str(int((blocked_until - datetime.utcnow()).total_seconds()))}
                )
            else:
                # Unblock
                del self.blocked[key]
        
        # Clean old requests
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=window_seconds)
        self.requests[key] = [
            (req_time, endpoint) for req_time, endpoint in self.requests[key]
            if req_time > cutoff
        ]
        
        # Check if limit exceeded
        request_count = len(self.requests[key])
        
        if request_count >= max_requests:
            logger.warning(f"Rate limit exceeded for {key}: {request_count}/{max_requests} in {window_seconds}s")
            
            # Block for exponential backoff
            backoff_seconds = min(300, window_seconds * (request_count // max_requests))
            blocked_until = now + timedelta(seconds=backoff_seconds)
            self.blocked[key] = (blocked_until, f"Too many requests ({request_count}/{max_requests})")
            
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Max {max_requests} requests per {window_seconds} seconds.",
                headers={"Retry-After": str(backoff_seconds)}
            )
        
        # Register request
        self.requests[key].append((now, f"{method} {path}"))
        
        return True
    
    def reset_key(self, key: str):
        """Reset rate limit for specific key"""
        if key in self.requests:
            del self.requests[key]
        if key in self.blocked:
            del self.blocked[key]


# Global rate limiter instance
rate_limiter = RateLimiter()


async def rate_limit_middleware(request: Request, call_next):
    """Middleware to apply rate limiting"""
    try:
        await rate_limiter.check_rate_limit(request)
    except HTTPException as e:
        return e
    
    response = await call_next(request)
    return response


# Header to indicate rate limit status
def add_rate_limit_headers(response, request: Request):
    """Add rate limit info to response headers"""
    path = request.url.path
    method = request.method
    rule = rate_limiter._get_rule(path, method)
    
    if rule:
        max_requests, window_seconds, key_type = rule
        key = rate_limiter._get_key(request, key_type)
        
        # Get current request count
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=window_seconds)
        current_count = len([
            (t, e) for t, e in rate_limiter.requests[key]
            if t > cutoff
        ])
        
        response.headers["X-RateLimit-Limit"] = str(max_requests)
        response.headers["X-RateLimit-Remaining"] = str(max(0, max_requests - current_count))
        response.headers["X-RateLimit-Reset"] = str(int((now + timedelta(seconds=window_seconds)).timestamp()))
    
    return response
