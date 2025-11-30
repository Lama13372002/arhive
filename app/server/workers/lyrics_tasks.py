"""Lyrics generation Celery tasks."""

from celery import current_task
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from celery import celery_app
from core.database import AsyncSessionLocal
from models.order import Order, OrderStatus
from models.lyrics_version import LyricsVersion
from schemas.order import LyricsGenerateRequest
from domain.lyrics_service import LyricsService
import structlog

logger = structlog.get_logger()


@celery_app.task(bind=True, name="workers.lyrics_tasks.generate_lyrics")
async def generate_lyrics_task(self, order_id: int, request_data: dict):
    """Generate lyrics for order."""
    
    task_id = self.request.id
    logger.info("Starting lyrics generation task", task_id=task_id, order_id=order_id)
    
    async with AsyncSessionLocal() as db:
        try:
            # Get order
            result = await db.execute(
                select(Order).where(Order.id == order_id)
            )
            order = result.scalar_one_or_none()
            
            if not order:
                logger.error("Order not found", order_id=order_id)
                return {"status": "error", "message": "Order not found"}
            
            # Update task progress
            current_task.update_state(
                state="PROGRESS",
                meta={"current": 1, "total": 3, "status": "Generating lyrics..."}
            )
            
            # Create lyrics service and generate
            lyrics_service = LyricsService(db)
            request = LyricsGenerateRequest(**request_data)
            
            lyrics_version = await lyrics_service.generate_lyrics_sync(order_id, request)
            
            # Update task progress
            current_task.update_state(
                state="PROGRESS",
                meta={"current": 2, "total": 3, "status": "Saving lyrics..."}
            )
            
            # Update order status
            order.status = OrderStatus.LYRICS_READY
            await db.commit()
            
            # Update task progress
            current_task.update_state(
                state="PROGRESS",
                meta={"current": 3, "total": 3, "status": "Complete"}
            )
            
            logger.info(
                "Lyrics generation completed",
                task_id=task_id,
                order_id=order_id,
                lyrics_version_id=lyrics_version.id
            )
            
            return {
                "status": "success",
                "order_id": order_id,
                "lyrics_version_id": lyrics_version.id,
                "version": lyrics_version.version
            }
            
        except Exception as e:
            logger.error(
                "Lyrics generation failed",
                task_id=task_id,
                order_id=order_id,
                error=str(e)
            )
            
            # Update order status to error
            try:
                order.status = OrderStatus.CANCELED
                await db.commit()
            except:
                pass
            
            return {
                "status": "error",
                "order_id": order_id,
                "message": str(e)
            }


@celery_app.task(name="workers.lyrics_tasks.regenerate_lyrics")
async def regenerate_lyrics_task(order_id: int, request_data: dict):
    """Regenerate lyrics for order."""
    
    logger.info("Starting lyrics regeneration task", order_id=order_id)
    
    async with AsyncSessionLocal() as db:
        try:
            # Get order
            result = await db.execute(
                select(Order).where(Order.id == order_id)
            )
            order = result.scalar_one_or_none()
            
            if not order:
                logger.error("Order not found", order_id=order_id)
                return {"status": "error", "message": "Order not found"}
            
            # Create lyrics service and regenerate
            lyrics_service = LyricsService(db)
            request = LyricsGenerateRequest(**request_data)
            
            lyrics_version = await lyrics_service.generate_lyrics_sync(order_id, request)
            
            logger.info(
                "Lyrics regeneration completed",
                order_id=order_id,
                lyrics_version_id=lyrics_version.id
            )
            
            return {
                "status": "success",
                "order_id": order_id,
                "lyrics_version_id": lyrics_version.id,
                "version": lyrics_version.version
            }
            
        except Exception as e:
            logger.error(
                "Lyrics regeneration failed",
                order_id=order_id,
                error=str(e)
            )
            
            return {
                "status": "error",
                "order_id": order_id,
                "message": str(e)
            }

