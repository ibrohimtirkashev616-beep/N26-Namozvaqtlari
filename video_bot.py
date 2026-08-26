"""
Telegram Universal Video Downloader Bot (aiogram 3 + yt-dlp)
Qo'llab-quvvatlanadigan tarmoqlar:
- 📸 Instagram (Reels, Post, IGTV)
- 📌 Pinterest (Pins, Videos)
- 🎵 TikTok (Videolar, Shorts)
- 👥 Facebook (Reels, Videos, Watch)
- ▶️ YouTube (Shorts, Videolar)
"""

import os
import sys
import logging
import asyncio
from dotenv import load_dotenv

# Windows konsolida Unicode/Emoji to'g'ri chiqishi uchun
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

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
from aiogram.exceptions import TelegramBadRequest, TelegramEntityTooLarge

# Downloader modulini import qilish
from downloader import (
    download_media,
    extract_first_url,
    detect_platform,
    get_platform_badge
)

# .env faylidan sozlamalarni yuklash
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Logging sozlamasi
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

dp = Dispatcher()

# Telegram Bot API maksimal fayl hajmi: 50MB (baytlarda)
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024


def format_size(size_bytes: int) -> str:
    """Fayl hajmini MB yoki KB ga aylantirish."""
    if size_bytes >= 1024 * 1024:
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


# ==========================================
# KOMANDALAR
# ==========================================

@dp.message(CommandStart())
async def cmd_start(message: Message):
    """/start komandasi uchun handler."""
    user_name = message.from_user.full_name if message.from_user else "Foydalanuvchi"
    text = (
        f"Assalomu alaykum, <b>{user_name}</b>! 👋\n\n"
        "Men <b>Universal Video Yuklovchi Botman</b> 📥\n\n"
        "Menga quyidagi ijtimoiy tarmoqlardan birining video havolasini (linkini) yuboring:\n"
        "• 📸 <b>Instagram</b> (Reels, Post)\n"
        "• 🎵 <b>TikTok</b> (Videolar)\n"
        "• 📌 <b>Pinterest</b> (Pin videolar)\n"
        "• 👥 <b>Facebook</b> (Reels, Watch)\n"
        "• ▶️ <b>YouTube</b> (Shorts, Videolar)\n\n"
        "🚀 <i>Shunchaki havolani bu yerga yuboring, men uni bir necha soniyada yuklab beraman!</i>"
    )
    await message.answer(text, parse_mode=ParseMode.HTML)


@dp.message(Command("help"))
async def cmd_help(message: Message):
    """/help komandasi uchun handler."""
    text = (
        "📖 <b>Botdan foydalanish bo'yicha qo'llanma:</b>\n\n"
        "1. Ijtimoiy tarmoqdagi videoning havolasini (linkini) nusxalang (Copy link).\n"
        "2. Havolani botga yuboring.\n"
        "3. Bot videoni avtomatik tarzda yuklab, sizga video shaklida yuboradi.\n\n"
        "⚠️ <b>Eslatmalar:</b>\n"
        "• Telegram boti maksimal <b>50 MB</b> gacha bo'lgan videolarni yubora oladi.\n"
        "• Yopiq (private) profillardan video yuklab bo'lmaydi.\n\n"
        "Savol yoki muammolar bo'lsa: @admin"
    )
    await message.answer(text, parse_mode=ParseMode.HTML)


# ==========================================
# HAVOLALARNI QAYTA ISHLASH (VIDEO YUKLASH)
# ==========================================

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

    # Foydalanuvchiga jarayon boshlanganini bildiramiz
    status_msg = await message.reply(
        f"⏳ <b>{badge}</b> havolasi qabul qilindi.\n"
        f"Video yuklanmoqda, iltimos kuting...",
        parse_mode=ParseMode.HTML
    )

    # Telegramda 'video yuklamoqda' animatsiyasini ko'rsatish
    await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.UPLOAD_VIDEO)

    downloaded_file_path = None

    try:
        # Asinxron tarzda videoni yuklab olamiz
        media_info = await download_media(url)
        downloaded_file_path = media_info.get("file_path")
        filesize = media_info.get("filesize", 0)

        # Fayl mavjudligini tekshiramiz
        if not downloaded_file_path or not os.path.exists(downloaded_file_path):
            await status_msg.edit_text(
                "❌ Kechirasiz, videoni yuklab olishning imkoni bo'lmadi.\n"
                "Havola yopiq akkauntga tegishli yoki o'chirilgan bo'lishi mumkin.",
                parse_mode=ParseMode.HTML
            )
            return

        # Hajm tekshiruvi (Telegram Bot API 50MB limiti)
        if filesize > MAX_FILE_SIZE_BYTES:
            await status_msg.edit_text(
                f"⚠️ <b>Video hajmi juda katta ({format_size(filesize)})!</b>\n\n"
                "Telegram botlari orqali maksimal 50 MB gacha bo'lgan videolarni yuborish mumkin.",
                parse_mode=ParseMode.HTML
            )
            return

        # Sarlavha va caption tayyorlash
        title = media_info.get("title", "Video")
        # Sarlavha juda uzun bo'lsa qisqartiramiz
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

        # Inline tugma (Asl havolaga o'tish)
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔗 Asl havola", url=url)]
            ]
        )

        # Telegramga yuklash statusini bildirish
        try:
            await status_msg.edit_text(
                f"📤 <b>{badge}</b> videosi yuklab olindi!\n"
                f"Telegramga yuborilmoqda, ozgina kuting...",
                parse_mode=ParseMode.HTML
            )
        except Exception:
            pass

        # Chat action yana yangilaymiz
        await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.UPLOAD_VIDEO)

        # Videoni foydalanuvchiga yuborish (timeout 300s)
        video_input = FSInputFile(downloaded_file_path)
        await message.reply_video(
            video=video_input,
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
            supports_streaming=True,
            request_timeout=300
        )

        # Status xabarini o'chirib tashlaymiz
        try:
            await status_msg.delete()
        except TelegramBadRequest:
            pass

    except Exception as e:
        logger.error(f"Video yuklashda xatolik: {e}", exc_info=True)
        try:
            await status_msg.edit_text(
                f"❌ <b>Xatolik yuz berdi:</b>\n"
                f"Videoni yuklab bo'lmadi yoki internet aloqasi sekin. Iltimos qaytadan urinib ko'ring.",
                parse_mode=ParseMode.HTML
            )
        except Exception:
            pass

    finally:
        # Xotirani tozalash: Fayl yuborib bo'lingach, 1 soniya kutib o'chiramiz
        if downloaded_file_path and os.path.exists(downloaded_file_path):
            await asyncio.sleep(1.5)
            try:
                os.remove(downloaded_file_path)
                logger.info(f"Vaqtincha fayl o'chirildi: {downloaded_file_path}")
            except OSError as err:
                logger.warning(f"Faylni o'chirishda xatolik: {err}")


# ==========================================
# ASOSIY ISHGA TUSHIRISH (MAIN)
# ==========================================

async def main():
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("\n" + "=" * 50)
        print("XATOLIK: BOT_TOKEN topilmadi!")
        print("Iltimos, .env fayliga Telegram bot tokeningizni kiriting:")
        print("BOT_TOKEN=1234567890:ABCdefGhIJKlmNoPQRsTUVwxyZ")
        print("=" * 50 + "\n")
        return

    # Katta hajmdagi videolarni yuklash uchun timeoutni 300 sekund (5 daqiqa) qilamiz
    session = AiohttpSession(timeout=300)
    bot = Bot(
        token=BOT_TOKEN,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # Bot komandalar menyusini o'rnatish
    await bot.set_my_commands([
        BotCommand(command="start", description="Botni ishga tushirish"),
        BotCommand(command="help", description="Yordam va qo'llanma"),
    ])

    bot_info = await bot.get_me()
    print(f"✅ Bot muvaffaqiyatli ishga tushdi: @{bot_info.username}")
    print("Video yuklashga tayyor...")

    # Pollingni boshlash
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\nBot to'xtatildi.")
