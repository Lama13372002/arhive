"""Health check endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from core.database import get_db
from core.redis import get_redis
import redis.asyncio as redis

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check."""
    return {"status": "ok"}


@router.get("/health/detailed")
async def detailed_health_check(
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
):
    """Detailed health check with dependencies."""
    health_status = {
        "status": "ok",
        "services": {}
    }
    
    # Check database
    try:
        await db.execute(text("SELECT 1"))
        health_status["services"]["database"] = "ok"
    except Exception as e:
        health_status["services"]["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check Redis
    try:
        await redis_client.ping()
        health_status["services"]["redis"] = "ok"
    except Exception as e:
        health_status["services"]["redis"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status

