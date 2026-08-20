"""
Telegram Bot - Main bot handler using aiogram 3.x
"""
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.orm import Session
from loguru import logger

from ..config import get_settings
from ..database import SessionLocal
from ..services.content import ContentService


class AdminState(StatesGroup):
    editing_content = State()


def create_content_keyboard(content_id: int) -> InlineKeyboardMarkup:
    """Create inline keyboard for content review"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ موافق", callback_data=f"approve:{content_id}"),
            InlineKeyboardButton(text="❌ رفض", callback_data=f"reject:{content_id}"),
        ],
        [
            InlineKeyboardButton(text="✏️ تعديل", callback_data=f"edit:{content_id}"),
            InlineKeyboardButton(text="🕐 جدولة", callback_data=f"schedule:{content_id}"),
        ],
    ])


async def cmd_start(message: types.Message):
    """Handle /start command"""
    await message.answer(
        "مرحباً بك في نظام MOS التسويقي! 🚀\n\n"
        "استخدم الأزرار للتنقل أو اختر من القوائم أدناه."
    )


async def cmd_status(message: types.Message):
    """Handle /status command"""
    db = SessionLocal()
    try:
        # Count contents by status
        from ..models import Content
        draft_count = db.query(Content).filter(Content.status == "draft").count()
        scheduled_count = db.query(Content).filter(Content.status == "scheduled").count()
        
        await message.answer(
            f"📊 حالة النظام:\n\n"
            f"• مسودات قيد المراجعة: {draft_count}\n"
            f"• محتوى مجدول: {scheduled_count}"
        )
    finally:
        db.close()


async def cmd_review(message: types.Message):
    """Handle /review command - show pending content"""
    db = SessionLocal()
    try:
        content_service = ContentService(db)
        contents = await content_service.review_pending_content()
        
        if not contents:
            await message.answer("لا يوجد محتوى قيد المراجعة ✅")
            return
        
        for content in contents[:5]:  # Limit to 5 at a time
            text = (
                f"📝 **محتوى جديد**\n\n"
                f"{content.text[:1000]}...\n\n"
                f"Hashtags: {', '.join(content.hashtags or [])}\n"
                f"Type: {content.content_type}"
            )
            
            await message.answer(
                text,
                reply_markup=create_content_keyboard(content.id),
                parse_mode="Markdown",
            )
    finally:
        db.close()


async def handle_callback(callback_query: types.CallbackQuery):
    """Handle inline button callbacks"""
    data = callback_query.data
    content_id = int(data.split(":")[1])
    action = data.split(":")[0]
    
    db = SessionLocal()
    try:
        content_service = ContentService(db)
        
        if action == "approve":
            success = await content_service.approve_content(content_id)
            response = "✅ تم الموافقة على المحتوى" if success else "❌ فشل الإجراء"
        
        elif action == "reject":
            success = await content_service.reject_content(content_id)
            response = "❌ تم رفض المحتوى" if success else "❌ فشل الإجراء"
        
        elif action == "edit":
            await callback_query.message.answer(
                "أرسل النص الجديد للتعديل:"
            )
            # Would need FSM state handling here
            response = "✏️ وضع التعديل مفعل (قيد التطوير)"
        
        elif action == "schedule":
            # For MVP, just approve and mark as scheduled
            success = await content_service.approve_content(content_id)
            response = "🕐 تم الجدولة للنشر" if success else "❌ فشل الإجراء"
        
        else:
            response = "❌ إجراء غير معروف"
        
        await callback_query.answer(response)
        
    finally:
        db.close()


def create_bot_router() -> Router:
    """Create and configure bot router"""
    router = Router()
    
    # Register handlers
    router.message.register(cmd_start, CommandStart())
    router.message.register(cmd_status, Command("status"))
    router.message.register(cmd_review, Command("review"))
    router.callback_query.register(handle_callback)
    
    return router


async def run_bot():
    """Run the Telegram bot"""
    settings = get_settings()
    
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("Telegram bot token not configured!")
        return
    
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(create_bot_router())
    
    logger.info("Starting Telegram bot...")
    await dp.start_polling(bot)
