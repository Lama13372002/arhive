"""Custom middleware for the application."""

import time
import structlog
from typing import Dict, Optional
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from core.config import settings
from core.redis import get_redis

logger = structlog.get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    """Structured logging middleware."""
    
    async def dispatch(self, request: Request, call_next):
        """Log request and response."""
        start_time = time.time()
        
        # Generate trace ID
        trace_id = f"trace_{int(time.time() * 1000)}"
        
        # Log request
        logger.info(
            "Request started",
            trace_id=trace_id,
            method=request.method,
            path=request.url.path,
            query_params=dict(request.query_params),
            user_agent=request.headers.get("user-agent"),
            client_ip=request.client.host if request.client else None,
        )
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log response
        logger.info(
            "Request completed",
            trace_id=trace_id,
            status_code=response.status_code,
            duration_ms=round(duration * 1000, 2),
        )
        
        # Add trace ID to response headers
        response.headers["X-Trace-ID"] = trace_id
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""
    
    def __init__(self, app, calls: int = None, period: int = 60):
        super().__init__(app)
        self.calls = calls or settings.rate_limit_per_minute
        self.period = period
    
    async def dispatch(self, request: Request, call_next):
        """Apply rate limiting."""
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/metrics"]:
            return await call_next(request)
        
        # Get client identifier
        client_ip = request.client.host if request.client else "unknown"
        user_id = getattr(request.state, "user_id", None)
        identifier = f"user:{user_id}" if user_id else f"ip:{client_ip}"
        
        # Check rate limit
        redis = await get_redis()
        key = f"rate_limit:{identifier}"
        
        try:
            # Get current count
            current = await redis.get(key)
            current = int(current) if current else 0
            
            if current >= self.calls:
                logger.warning(
                    "Rate limit exceeded",
                    identifier=identifier,
                    current=current,
                    limit=self.calls,
                )
                
                return JSONResponse(
                    status_code=429,
                    content={
                        "error_code": "RATE_LIMIT_EXCEEDED",
                        "message": f"Rate limit exceeded. Maximum {self.calls} requests per {self.period} seconds.",
                    },
                    headers={
                        "Retry-After": str(self.period),
                        "X-RateLimit-Limit": str(self.calls),
                        "X-RateLimit-Remaining": "0",
                    }
                )
            
            # Increment counter
            pipe = redis.pipeline()
            pipe.incr(key)
            pipe.expire(key, self.period)
            await pipe.execute()
            
            # Add rate limit headers
            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(self.calls)
            response.headers["X-RateLimit-Remaining"] = str(self.calls - current - 1)
            
            return response
            
        except Exception as e:
            logger.error("Rate limit check failed", error=str(e))
            # If Redis is down, allow the request
            return await call_next(request)

