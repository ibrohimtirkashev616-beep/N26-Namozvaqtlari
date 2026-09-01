"""
Telegram Universal Video Downloader Bot (aiogram 3 + yt-dlp + Local Bot API Server)
Limit: 2000 MB (2 GB) gacha bo'lgan videolarni yuklash
"""

import os
import sys
import logging
import asyncio
from dotenv import load_dotenv

# Windows konsolida Unicode/Emoji to'g'ri chiqishi uchun
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Script papkasini import yo'liga qo'shish
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    FSInputFile,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    BotCommand
)
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode, ChatAction
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.exceptions import TelegramBadRequest

# Downloader modulini import qilish
from downloader import (
    download_media,
    extract_first_url,
    detect_platform,
    get_platform_badge
)

# .env faylidan sozlamalarni yuklash
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

raw_token = os.getenv("VIDEO_BOT_TOKEN") or os.getenv("BOT_TOKEN") or "8847541613:AAHLQMc5o1VRtOsvHGMvp0dA5y-KbL-m3mo"
BOT_TOKEN = raw_token.strip().replace(" ", "").replace("\n", "").replace("\r", "")

# Local Telegram Bot API server sozlamalari
USE_LOCAL_BOT_API = os.getenv("USE_LOCAL_BOT_API", "true").lower() in ("true", "1", "yes")
LOCAL_BOT_API_URL = os.getenv("LOCAL_BOT_API_URL", "http://localhost:8081").strip()

# Maksimal fayl hajmi: 2000 MB (2 GB)
MAX_FILE_SIZE_BYTES = 2000 * 1024 * 1024

# Logging sozlamasi
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

IS_LOCAL_API_ACTIVE = False

dp = Dispatcher()


def format_size(size_bytes: int) -> str:
    """Fayl hajmini MB yoki GB ga aylantirish."""
    if size_bytes >= 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
    elif size_bytes >= 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    elif size_bytes >= 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes} B"


def format_duration(seconds: int) -> str:
    """Davomiylikni mm:ss yoki hh:mm:ss formatida chiqarish."""
    if not seconds:
        return "Noma'lum"
    mins, secs = divmod(int(seconds), 60)
    hours, mins = divmod(mins, 60)
    if hours > 0:
        return f"{hours:02d}:{mins:02d}:{secs:02d}"
    return f"{mins:02d}:{secs:02d}"


@dp.message(CommandStart())
async def cmd_start(message: Message):
    """/start komandasi uchun handler."""
    user_name = message.from_user.full_name if message.from_user else "Foydalanuvchi"
    limit_text = "2 GB (2000 MB)" if IS_LOCAL_API_ACTIVE else "50 MB"
    text = (
        f"Assalomu alaykum, <b>{user_name}</b>! 👋\n\n"
        "Men <b>Universal Video Yuklovchi Botman</b> 📥\n\n"
        "Menga quyidagi ijtimoiy tarmoqlardan birining video linkini yuboring:\n"
        "• 📸 <b>Instagram</b> (Reels, Post)\n"
        "• 🎵 <b>TikTok</b> (Videolar)\n"
        "• 📌 <b>Pinterest</b> (Pin videolar)\n"
        "• 👥 <b>Facebook</b> (Reels, Watch)\n"
        "• ▶️ <b>YouTube</b> (Shorts, Videolar)\n\n"
        "🚀 <i>Shunchaki linkni bu yerga tashlang, men videoni yuklab beraman!</i>"
    )
    await message.answer(text, parse_mode=ParseMode.HTML)


@dp.message(Command("help"))
async def cmd_help(message: Message):
    """/help komandasi uchun handler."""
    limit_text = "2 GB" if IS_LOCAL_API_ACTIVE else "50 MB"
    text = (
        "📖 <b>Botdan foydalanish bo'yicha qo'llanma:</b>\n\n"
        "1. Ijtimoiy tarmoqdagi videoning havolasini (linkini) nusxalang (Copy link).\n"
        "2. Havolani botga yuboring.\n"
        "3. Bot videoni avtomatik yuklab sizga taqdim etadi.\n\n"
        "⚠️ <b>Eslatmalar:</b>\n"
        f"• Telegram orqali maksimal <b>{limit_text}</b> gacha bo'lgan videolarni yuborish mumkin.\n"
        "• Yopiq (private) akkauntlardagi videolarni yuklab bo'lmaydi."
    )
    await message.answer(text, parse_mode=ParseMode.HTML)


@dp.message(F.text)
async def handle_text_message(message: Message, bot: Bot):
    """Foydalanuvchi yuborgan matn ichidan havolani topib videoni yuklash."""
    text = message.text.strip()
    url = extract_first_url(text)

    if not url:
        await message.answer(
            "Iltimos, to'g'ri video havolasini (link) yuboring! 🔗\n"
            "Masalan: Instagram, TikTok, Pinterest, Facebook yoki YouTube linki.",
            parse_mode=ParseMode.HTML
        )
        return

    platform = detect_platform(url)
    badge = get_platform_badge(platform)

    status_msg = await message.reply(
        f"⏳ <b>{badge}</b> havolasi qabul qilindi.\n"
        f"Video yuklanmoqda, iltimos kuting...",
        parse_mode=ParseMode.HTML
    )

    await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.UPLOAD_VIDEO)

    downloaded_file_path = None
    max_mb = 2000 if IS_LOCAL_API_ACTIVE else 48
    max_allowed_bytes = (2000 if IS_LOCAL_API_ACTIVE else 49) * 1024 * 1024

    try:
        media_info = await download_media(url, max_filesize_mb=max_mb)
        downloaded_file_path = media_info.get("file_path")
        filesize = media_info.get("filesize", 0)

        if not downloaded_file_path or not os.path.exists(downloaded_file_path):
            await status_msg.edit_text(
                "❌ Kechirasiz, videoni yuklab olishning imkoni bo'lmadi.\n"
                "Havola yopiq akkauntga tegishli yoki o'chirilgan bo'lishi mumkin.",
                parse_mode=ParseMode.HTML
            )
            return

        if filesize > max_allowed_bytes:
            if not IS_LOCAL_API_ACTIVE:
                await status_msg.edit_text(
                    f"⚠️ <b>Video hajmi juda katta ({format_size(filesize)})!</b>\n\n"
                    "Telegram boti orqali maksimal <b>50 MB</b> gacha bo'lgan videolarni yuborish mumkin.\n"
                    "💡 <i>(Bu video davomiyligi juda uzun bo'lgani uchun 50 MB dan oshib ketdi).</i>",
                    parse_mode=ParseMode.HTML
                )
            else:
                await status_msg.edit_text(
                    f"⚠️ <b>Video hajmi juda katta ({format_size(filesize)})!</b>\n\n"
                    f"Maksimal ruxsat etilgan hajm: {format_size(max_allowed_bytes)}.",
                    parse_mode=ParseMode.HTML
                )
            return

        title = media_info.get("title", "Video")
        if len(title) > 60:
            title = title[:57] + "..."
        
        duration_str = format_duration(media_info.get("duration", 0))
        size_str = format_size(filesize)

        caption = (
            f"🎬 <b>{title}</b>\n\n"
            f"🌐 Manba: <b>{badge}</b>\n"
            f"⏱ Davomiyligi: <code>{duration_str}</code>\n"
            f"📦 Hajmi: <code>{size_str}</code>\n\n"
            f"🤖 @{(await bot.get_me()).username or 'VideoDownloaderBot'}"
        )

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔗 Asl havola", url=url)]
            ]
        )

        try:
            await status_msg.edit_text(
                f"📤 <b>{badge}</b> videosi yuklab olindi!\n"
                f"Telegramga yuborilmoqda, ozgina kuting...",
                parse_mode=ParseMode.HTML
            )
        except Exception:
            pass

        await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.UPLOAD_VIDEO)

        video_input = FSInputFile(downloaded_file_path)
        await message.reply_video(
            video=video_input,
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
            supports_streaming=True,
            request_timeout=600
        )

        try:
            await status_msg.delete()
        except TelegramBadRequest:
            pass

    except Exception as e:
        logger.error(f"Video yuklashda xatolik: {e}", exc_info=True)
        try:
            await status_msg.edit_text(
                "❌ <b>Xatolik yuz berdi:</b>\n"
                "Videoni yuklab bo'lmadi yoki internet sekin. Iltimos qaytadan urinib ko'ring.",
                parse_mode=ParseMode.HTML
            )
        except Exception:
            pass

    finally:
        if downloaded_file_path and os.path.exists(downloaded_file_path):
            await asyncio.sleep(1.5)
            try:
                os.remove(downloaded_file_path)
                logger.info(f"Vaqtincha fayl o'chirildi: {downloaded_file_path}")
            except OSError as err:
                logger.warning(f"Faylni o'chirishda xatolik: {err}")


async def is_local_api_running(url: str) -> bool:
    """Local Telegram Bot API server ishlayotganini tekshirish."""
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=1.5)) as resp:
                return resp.status in (200, 400, 404)
    except Exception:
        return False


async def main():
    global IS_LOCAL_API_ACTIVE
    session = AiohttpSession(timeout=600)
    
    local_server_active = False
    if USE_LOCAL_BOT_API:
        if await is_local_api_running(LOCAL_BOT_API_URL):
            local_server_active = True
        else:
            logger.warning(f"⚠️ {LOCAL_BOT_API_URL} ga ulanib bo'lmadi (Docker yoqilmagan). Standart api.telegram.org ga ulanmoqda...")

    IS_LOCAL_API_ACTIVE = local_server_active

    if local_server_active:
        custom_server = TelegramAPIServer.from_base(LOCAL_BOT_API_URL, is_local=True)
        bot = Bot(
            token=BOT_TOKEN,
            session=session,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
            server=custom_server
        )
        logger.info(f"🚀 Local Telegram Bot API serveriga ulandi: {LOCAL_BOT_API_URL} (2GB Limit)")
    else:
        bot = Bot(
            token=BOT_TOKEN,
            session=session,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        logger.info("🌐 Rasmiy Telegram Bot API (api.telegram.org) ga ulandi (50MB Limit)")

    await bot.set_my_commands([
        BotCommand(command="start", description="Botni ishga tushirish"),
        BotCommand(command="help", description="Yordam va qo'llanma"),
    ])

    bot_info = await bot.get_me()
    print(f"✅ Bot muvaffaqiyatli ishga tushdi: @{bot_info.username}")
    print(f"Fayl limiti: {'2000 MB (Local API)' if USE_LOCAL_BOT_API else '50 MB (Official API)'}")

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\nBot to'xtatildi.")
