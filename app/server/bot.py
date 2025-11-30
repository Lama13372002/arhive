"""Telegram bot implementation."""

import structlog
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from core.config import settings
from core.database import AsyncSessionLocal
from models.user import User
from domain.auth_service import AuthService
from workers.notification_tasks import send_welcome_message_task

logger = structlog.get_logger()

# Initialize bot and dispatcher
bot = Bot(settings.telegram_bot_token)
dp = Dispatcher()


class BotStates(StatesGroup):
    """Bot states."""
    waiting_for_input = State()


@dp.message(CommandStart())
async def start_command(message: Message, state: FSMContext):
    """Handle /start command."""
    user = message.from_user
    
    logger.info("User started bot", user_id=user.id, username=user.username)
    
    # Get or create user in database
    async with AsyncSessionLocal() as db:
        auth_service = AuthService(db)
        db_user = await auth_service.get_or_create_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            language_code=user.language_code or "ru"
        )
    
    # Create welcome message
    welcome_text = (
        f"Привет, {user.first_name or 'друг'}! 👋\n\n"
        "Добро пожаловать в Sunog - AI генератор персональных песен! 🎵\n\n"
        "Я помогу вам создать уникальную песню для любого повода:\n"
        "• День рождения\n"
        "• Свадьба\n"
        "• Признание в любви\n"
        "• И многое другое!\n\n"
        "Нажмите кнопку ниже, чтобы начать создание песни:"
    )
    
    # Create inline keyboard with Mini App button
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🎵 Создать песню",
            web_app=WebAppInfo(url=f"{settings.frontend_url}")
        )],
        [InlineKeyboardButton(
            text="📋 Мои заказы",
            web_app=WebAppInfo(url=f"{settings.frontend_url}/orders")
        )],
        [InlineKeyboardButton(
            text="ℹ️ Помощь",
            callback_data="help"
        )]
    ])
    
    await message.answer(welcome_text, reply_markup=keyboard)
    await state.set_state(BotStates.waiting_for_input)


@dp.message(Command("help"))
async def help_command(message: Message):
    """Handle /help command."""
    help_text = (
        "🎵 <b>Sunog - AI генератор песен</b>\n\n"
        "Доступные команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать эту справку\n"
        "/orders - Открыть список заказов\n"
        "/new - Создать новый заказ\n\n"
        "Как это работает:\n"
        "1. Нажмите 'Создать песню'\n"
        "2. Заполните форму с пожеланиями\n"
        "3. Получите черновик текста\n"
        "4. Отредактируйте при необходимости\n"
        "5. Получите готовую песню!\n\n"
        "Поддержка: @your_support_username"
    )
    
    await message.answer(help_text, parse_mode="HTML")


@dp.message(Command("orders"))
async def orders_command(message: Message):
    """Handle /orders command."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📋 Открыть заказы",
            web_app=WebAppInfo(url=f"{settings.frontend_url}/orders")
        )]
    ])
    
    await message.answer(
        "Откройте приложение, чтобы просмотреть ваши заказы:",
        reply_markup=keyboard
    )


@dp.message(Command("new"))
async def new_command(message: Message):
    """Handle /new command."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🎵 Создать новую песню",
            web_app=WebAppInfo(url=f"{settings.frontend_url}")
        )]
    ])
    
    await message.answer(
        "Создайте новую песню:",
        reply_markup=keyboard
    )


@dp.callback_query(F.data == "help")
async def help_callback(callback: CallbackQuery):
    """Handle help callback."""
    help_text = (
        "🎵 <b>Как пользоваться Sunog:</b>\n\n"
        "1. <b>Создание песни:</b>\n"
        "   • Нажмите 'Создать песню'\n"
        "   • Выберите жанр, настроение, язык\n"
        "   • Укажите повод и получателя\n"
        "   • Добавьте ключевые фразы\n\n"
        "2. <b>Редактирование:</b>\n"
        "   • Просмотрите сгенерированный текст\n"
        "   • Внесите правки при необходимости\n"
        "   • Утвердите финальную версию\n\n"
        "3. <b>Получение результата:</b>\n"
        "   • Скачайте текст песни\n"
        "   • Получите аудио версию (если доступно)\n\n"
        "💡 <b>Советы:</b>\n"
        "• Будьте конкретны в описании\n"
        "• Укажите особые пожелания\n"
        "• Можете редактировать текст несколько раз\n\n"
        "❓ <b>Поддержка:</b> @your_support_username"
    )
    
    await callback.message.edit_text(help_text, parse_mode="HTML")


@dp.message()
async def handle_message(message: Message, state: FSMContext):
    """Handle other messages."""
    current_state = await state.get_state()
    
    if current_state == BotStates.waiting_for_input:
        # User sent some text, suggest creating a song
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🎵 Создать песню",
                web_app=WebAppInfo(url=f"{settings.frontend_url}")
            )]
        ])
        
        await message.answer(
            "Отлично! Давайте создадим для вас песню. Нажмите кнопку ниже:",
            reply_markup=keyboard
        )
    else:
        # Default response
        await message.answer(
            "Используйте команды или кнопки для навигации. /help для справки."
        )


async def setup_webhook():
    """Setup webhook for production."""
    if settings.telegram_webhook_url:
        webhook_url = f"{settings.telegram_webhook_url}/bot/webhook"
        await bot.set_webhook(
            url=webhook_url,
            secret_token=settings.telegram_bot_webhook_secret
        )
        logger.info("Webhook set up", webhook_url=webhook_url)


async def remove_webhook():
    """Remove webhook for development."""
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Webhook removed")


def create_webhook_app() -> web.Application:
    """Create webhook application."""
    app = web.Application()
    
    # Setup webhook handler
    webhook_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=settings.telegram_bot_webhook_secret
    )
    webhook_handler.register(app, path="/bot/webhook")
    
    # Setup application
    setup_application(app, dp, bot=bot)
    
    return app


async def start_polling():
    """Start bot polling (for development)."""
    logger.info("Starting bot polling")
    await dp.start_polling(bot)


async def stop_bot():
    """Stop bot."""
    await bot.session.close()
    logger.info("Bot stopped")


# Bot startup/shutdown events
@dp.startup()
async def on_startup():
    """Bot startup event."""
    logger.info("Bot startup")
    if not settings.debug:
        await setup_webhook()


@dp.shutdown()
async def on_shutdown():
    """Bot shutdown event."""
    logger.info("Bot shutdown")
    if not settings.debug:
        await remove_webhook()
    await stop_bot()

