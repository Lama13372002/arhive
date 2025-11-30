"""Audio generation Celery tasks."""

from celery import current_task
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from celery import celery_app
from core.database import AsyncSessionLocal
from models.order import Order, OrderStatus
from models.lyrics_version import LyricsVersion
from models.audio_asset import AudioAsset, AudioStatus
from integrations.audio.suno_client import SunoClient
from core.config import settings
import structlog

logger = structlog.get_logger()


@celery_app.task(bind=True, name="workers.audio_tasks.generate_audio")
async def generate_audio_task(self, order_id: int, audio_asset_id: int):
    """Generate audio for order."""
    
    task_id = self.request.id
    logger.info("Starting audio generation task", task_id=task_id, order_id=order_id, audio_asset_id=audio_asset_id)
    
    async with AsyncSessionLocal() as db:
        try:
            # Get order and audio asset
            result = await db.execute(
                select(Order).where(Order.id == order_id)
            )
            order = result.scalar_one_or_none()
            
            if not order:
                logger.error("Order not found", order_id=order_id)
                return {"status": "error", "message": "Order not found"}
            
            result = await db.execute(
                select(AudioAsset).where(AudioAsset.id == audio_asset_id)
            )
            audio_asset = result.scalar_one_or_none()
            
            if not audio_asset:
                logger.error("Audio asset not found", audio_asset_id=audio_asset_id)
                return {"status": "error", "message": "Audio asset not found"}
            
            # Update task progress
            current_task.update_state(
                state="PROGRESS",
                meta={"current": 1, "total": 4, "status": "Preparing audio generation..."}
            )
            
            # Get latest lyrics
            result = await db.execute(
                select(LyricsVersion)
                .where(LyricsVersion.order_id == order_id)
                .order_by(LyricsVersion.version.desc())
                .limit(1)
            )
            lyrics_version = result.scalar_one_or_none()
            
            if not lyrics_version:
                logger.error("No lyrics found for order", order_id=order_id)
                return {"status": "error", "message": "No lyrics found"}
            
            # Update audio asset status
            audio_asset.status = AudioStatus.GENERATING
            await db.commit()
            
            # Update task progress
            current_task.update_state(
                state="PROGRESS",
                meta={"current": 2, "total": 4, "status": "Generating audio with Suno..."}
            )
            
            # Generate audio with Suno
            if settings.use_suno:
                suno_client = SunoClient()
                
                # Build prompt for Suno
                prompt = f"{order.genre or 'pop'}, {order.mood or 'romantic'}, {order.tempo or 'medium tempo'}, language: {order.language.value}"
                
                # Generate music
                result = await suno_client.generate_music(
                    lyrics=lyrics_version.text,
                    prompt=prompt,
                    title=f"Song for {order.recipient or 'friend'}",
                    style=prompt,
                    callback_url=f"{settings.public_base_url}/api/v1/audio/callback"
                )
                
                # Update task progress
                current_task.update_state(
                    state="PROGRESS",
                    meta={"current": 3, "total": 4, "status": "Processing audio..."}
                )
                
                # Poll for completion
                poll_result = await suno_client.poll_generation_status(
                    result["task_id"],
                    timeout_seconds=420
                )
                
                if poll_result["status"] == "completed":
                    # Update audio asset with URLs
                    audio_urls = poll_result.get("audio_urls", [])
                    if audio_urls:
                        audio_asset.url = audio_urls[0]  # Use first URL
                        audio_asset.meta = {
                            "all_urls": audio_urls,
                            "suno_task_id": result["task_id"],
                            "generation_mode": result["mode"]
                        }
                        audio_asset.status = AudioStatus.READY
                        
                        # Update order status
                        order.status = OrderStatus.DELIVERED
                        
                        logger.info(
                            "Audio generation completed",
                            task_id=task_id,
                            order_id=order_id,
                            audio_asset_id=audio_asset_id,
                            urls_count=len(audio_urls)
                        )
                    else:
                        audio_asset.status = AudioStatus.FAILED
                        logger.error("No audio URLs returned from Suno", order_id=order_id)
                else:
                    audio_asset.status = AudioStatus.FAILED
                    logger.error("Suno generation failed", order_id=order_id, result=poll_result)
            else:
                # Suno disabled, mark as failed
                audio_asset.status = AudioStatus.FAILED
                logger.warning("Suno integration disabled", order_id=order_id)
            
            await db.commit()
            
            # Update task progress
            current_task.update_state(
                state="PROGRESS",
                meta={"current": 4, "total": 4, "status": "Complete"}
            )
            
            return {
                "status": "success",
                "order_id": order_id,
                "audio_asset_id": audio_asset_id,
                "audio_status": audio_asset.status.value
            }
            
        except Exception as e:
            logger.error(
                "Audio generation failed",
                task_id=task_id,
                order_id=order_id,
                audio_asset_id=audio_asset_id,
                error=str(e)
            )
            
            # Update audio asset status to failed
            try:
                audio_asset.status = AudioStatus.FAILED
                await db.commit()
            except:
                pass
            
            return {
                "status": "error",
                "order_id": order_id,
                "audio_asset_id": audio_asset_id,
                "message": str(e)
            }


@celery_app.task(name="workers.audio_tasks.process_suno_callback")
async def process_suno_callback_task(callback_data: dict):
    """Process Suno webhook callback."""
    
    logger.info("Processing Suno callback", callback_data=callback_data)
    
    try:
        task_id = callback_data.get("taskId")
        if not task_id:
            logger.error("No taskId in Suno callback")
            return {"status": "error", "message": "No taskId"}
        
        # Extract audio URLs
        suno_client = SunoClient()
        urls = suno_client.extract_audio_urls(callback_data)
        
        if urls:
            logger.info("Suno callback processed successfully", task_id=task_id, urls_count=len(urls))
            return {
                "status": "success",
                "task_id": task_id,
                "audio_urls": urls
            }
        else:
            logger.warning("No audio URLs in Suno callback", task_id=task_id)
            return {
                "status": "warning",
                "task_id": task_id,
                "message": "No audio URLs found"
            }
            
    except Exception as e:
        logger.error("Suno callback processing failed", error=str(e))
        return {
            "status": "error",
            "message": str(e)
        }

