from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from app.config import settings
import logging

logger = logging.getLogger(__name__)

def get_client_ip_for_limiter(request: Request) -> str:
    """Extract client IP for rate limiting, considering proxies."""
    # Check for X-Forwarded-For header (most common with reverse proxies)
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        # Take the first IP in the chain (original client)
        ip = x_forwarded_for.split(",")[0].strip()
        return ip
    
    # Check for X-Real-IP header (Nginx)
    x_real_ip = request.headers.get("x-real-ip")
    if x_real_ip:
        return x_real_ip
    
    # Check for CF-Connecting-IP (Cloudflare)
    cf_connecting_ip = request.headers.get("cf-connecting-ip")
    if cf_connecting_ip:
        return cf_connecting_ip
    
    # Fallback to standard method
    return get_remote_address(request)

# Create rate limiter instance
limiter = Limiter(
    key_func=get_client_ip_for_limiter,
    default_limits=[f"{settings.rate_limit_requests}/{settings.rate_limit_window}second"]
)

# Custom rate limit exceeded handler
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded."""
    logger.warning(f"Rate limit exceeded for IP: {get_client_ip_for_limiter(request)}")
    return await _rate_limit_exceeded_handler(request, exc)
