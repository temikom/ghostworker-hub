"""Rate limiting configuration"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.config import settings


def get_user_identifier(request: Request) -> str:
    """Get identifier for rate limiting - user ID or IP"""
    # Try to get user from authorization header
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        # Use token hash as identifier for authenticated users
        token = auth_header[7:]
        return f"user:{token[:16]}"
    
    # Fall back to IP address
    return get_remote_address(request)


limiter = Limiter(
    key_func=get_user_identifier,
    default_limits=[f"{settings.RATE_LIMIT_REQUESTS}/minute"],
    storage_uri=settings.REDIS_URL,
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Handler for rate limit exceeded"""
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded. Please try again later.",
            "retry_after": exc.detail
        }
    )
