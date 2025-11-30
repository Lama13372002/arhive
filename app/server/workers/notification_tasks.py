"""Notification Celery tasks."""

from celery import celery_app
from aiogram import Bot
from core.config import settings
import structlog

logger = structlog.get_logger()

# Initialize bot
bot = Bot(settings.telegram_bot_token)


@celery_app.task(name="workers.notification_tasks.send_notification")
async def send_notification_task(telegram_id: int, message: str, reply_markup: dict = None):
    """Send notification to Telegram user."""
    
    logger.info("Sending notification", telegram_id=telegram_id, message=message[:100])
    
    try:
        # Send message
        await bot.send_message(
            chat_id=telegram_id,
            text=message,
            reply_markup=reply_markup
        )
        
        logger.info("Notification sent successfully", telegram_id=telegram_id)
        return {"status": "success", "telegram_id": telegram_id}
        
    except Exception as e:
        logger.error("Notification sending failed", telegram_id=telegram_id, error=str(e))
        return {"status": "error", "telegram_id": telegram_id, "message": str(e)}


@celery_app.task(name="workers.notification_tasks.send_audio_notification")
async def send_audio_notification_task(telegram_id: int, audio_url: str, caption: str = None):
    """Send audio notification to Telegram user."""
    
    logger.info("Sending audio notification", telegram_id=telegram_id, audio_url=audio_url)
    
    try:
        # Send audio
        await bot.send_audio(
            chat_id=telegram_id,
            audio=audio_url,
            caption=caption or "Ваша песня готова! 🎵"
        )
        
        logger.info("Audio notification sent successfully", telegram_id=telegram_id)
        return {"status": "success", "telegram_id": telegram_id}
        
    except Exception as e:
        logger.error("Audio notification sending failed", telegram_id=telegram_id, error=str(e))
        return {"status": "error", "telegram_id": telegram_id, "message": str(e)}


@celery_app.task(name="workers.notification_tasks.send_order_status_update")
async def send_order_status_update_task(telegram_id: int, order_id: int, status: str, message: str = None):
    """Send order status update notification."""
    
    status_messages = {
        "lyrics_ready": "🎵 Текст вашей песни готов! Откройте приложение, чтобы просмотреть и отредактировать его.",
        "approved": "✅ Заказ утвержден! Начинаем генерацию аудио...",
        "generating": "🎼 Генерируем аудио для вашей песни...",
        "delivered": "🎉 Ваша песня готова! Откройте приложение, чтобы скачать результат.",
        "canceled": "❌ Заказ отменен. Если это ошибка, обратитесь в поддержку."
    }
    
    notification_message = message or status_messages.get(status, f"Статус заказа изменен: {status}")
    
    # Create inline keyboard with "Открыть заказ" button
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Открыть заказ",
            web_app={"url": f"{settings.frontend_url}/orders/{order_id}"}
        )]
    ])
    
    return await send_notification_task.delay(telegram_id, notification_message, reply_markup.to_python())


@celery_app.task(name="workers.notification_tasks.send_welcome_message")
async def send_welcome_message_task(telegram_id: int, username: str = None):
    """Send welcome message to new user."""
    
    name = username or "друг"
    message = (
        f"Привет, {name}! 👋\n\n"
        "Добро пожаловать в Sunog - AI генератор персональных песен! 🎵\n\n"
        "Я помогу вам создать уникальную песню для любого повода:\n"
        "• День рождения\n"
        "• Свадьба\n"
        "• Признание в любви\n"
        "• И многое другое!\n\n"
        "Нажмите кнопку ниже, чтобы начать создание песни:"
    )
    
    # Create inline keyboard with "Создать песню" button
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🎵 Создать песню",
            web_app={"url": f"{settings.frontend_url}"}
        )]
    ])
    
    return await send_notification_task.delay(telegram_id, message, reply_markup.to_python())

