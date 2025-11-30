"""Cleanup Celery tasks."""

from celery import celery_app
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from datetime import datetime, timedelta

from core.database import AsyncSessionLocal
from models.audio_asset import AudioAsset
from models.lyrics_version import LyricsVersion
from core.config import settings
import structlog

logger = structlog.get_logger()


@celery_app.task(name="workers.cleanup_tasks.cleanup_expired_assets")
async def cleanup_expired_assets():
    """Clean up expired assets older than retention period."""
    
    logger.info("Starting cleanup of expired assets")
    
    async with AsyncSessionLocal() as db:
        try:
            # Calculate cutoff date
            cutoff_date = datetime.utcnow() - timedelta(days=settings.asset_retention_days)
            
            # Clean up old audio assets
            result = await db.execute(
                select(AudioAsset).where(AudioAsset.created_at < cutoff_date)
            )
            old_audio_assets = result.scalars().all()
            
            for asset in old_audio_assets:
                # In a real implementation, delete from S3 storage here
                logger.info(f"Cleaning up audio asset {asset.id}")
            
            # Delete old audio assets from database
            await db.execute(
                delete(AudioAsset).where(AudioAsset.created_at < cutoff_date)
            )
            
            # Clean up old lyrics versions (keep only latest 5 per order)
            # This is a more complex query that would need to be implemented
            # based on specific business requirements
            
            await db.commit()
            
            logger.info(
                "Cleanup completed",
                audio_assets_cleaned=len(old_audio_assets),
                cutoff_date=cutoff_date.isoformat()
            )
            
            return {
                "status": "success",
                "audio_assets_cleaned": len(old_audio_assets),
                "cutoff_date": cutoff_date.isoformat()
            }
            
        except Exception as e:
            logger.error("Cleanup failed", error=str(e))
            return {
                "status": "error",
                "message": str(e)
            }

