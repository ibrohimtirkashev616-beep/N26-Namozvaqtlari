"""
AI HR Agent Telegram Boti - Asosiy ishga tushirish fayli
Nomzodlar arizalarini OpenAI orqali tahlil qilish, mos keladiganini saralash
va barcha arizalarni HR guruhiga avtomatik yuborish tizimi.
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# Windows konsolida UTF-8 ni to'g'ri ko'rsatish
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Papka yo'lini Python importlariga qo'shish
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import config
from services.database import init_db
from handlers.common import router as common_router
from handlers.candidate import router as candidate_router
from handlers.admin import router as admin_router

# Logging sozlamalari
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("HR_Agent")


async def set_main_menu_commands(bot: Bot):
    """Telegram menyusiga asosiy buyruqlarni o'rnatish."""
    commands = [
        BotCommand(command="start", description="🤖 Botni qayta ishga tushirish"),
        BotCommand(command="help", description="ℹ️ Yordam va bot haqida"),
        BotCommand(command="stats", description="📊 HR statistikasi"),
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())


async def main():
    """Botning asosiy boshqaruv sikli."""
    logger.info("=" * 55)
    logger.info("  🚀 AI HR AGENT TELEGRAM BOT ISHGA TUSHMOQDA...")
    logger.info("=" * 55)
    
    if not config.BOT_TOKEN:
        logger.critical("XATOLIK: .env faylida BOT_TOKEN topilmadi!")
        return
        
    if not config.OPENAI_API_KEY:
        logger.warning("OGOHLANTIRISH: .env faylida OPENAI_API_KEY ko'rsatilmagan!")

    # 1. Ma'lumotlar bazasini initsializatsiya qilish
    await init_db()

    # 2. Bot va Dispatcher obyektlari
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # 3. Routerlarni ro'yxatdan o'tkazish
    dp.include_router(common_router)
    dp.include_router(candidate_router)
    dp.include_router(admin_router)

    # 4. Bot ma'lumotlarini olish va menyuni sozlash
    try:
        bot_info = await bot.get_me()
        logger.info(f"Bot muvaffaqiyatli ulandi: @{bot_info.username} (ID: {bot_info.id})")
        logger.info(f"HR Guruh ID: {config.HR_GROUP_ID}")
        logger.info(f"AI Model: {config.OPENAI_MODEL}")
        
        await set_main_menu_commands(bot)
    except Exception as e:
        logger.error(f"Bot ulanishida xatolik: {e}")

    # 5. Eski yangilanishlarni (updates) tozalash va pollingni boshlash
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bot xabarlarni qabul qilishga tayyor! (Polling boshlandi)")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Bot to'xtatildi.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot qo'lda to'xtatildi.")
