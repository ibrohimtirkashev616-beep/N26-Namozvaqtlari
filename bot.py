"""
Telegram Kalkulyator Boti (aiogram 3)
Foydalanuvchi kiritgan matematik ifodalarni hisoblab beruvchi va
interaktiv inline kalkulyatorga ega bot.
"""

import os
import sys
import logging
import asyncio
import re
from dotenv import load_dotenv

# Windows konsolida emoji va unicode to'g'ri chiqishi uchun
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, BotCommand
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramBadRequest

# Script joylashgan papkani import yo'liga qo'shish
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from calculator import evaluate_math, CONSTANTS, MATH_FUNCTIONS
from keyboards import get_calculator_keyboard, get_main_reply_keyboard

# .env faylidan sozlamalarni yuklash
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Logging sozlamasi
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Dispatcher yaratish
dp = Dispatcher()


def format_calc_screen(expression: str) -> str:
    """Kalkulyator ekrani uchun matn formatlash."""
    return (
        "🧮 <b>Interaktiv Kalkulyator</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"<code>{expression}</code>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "<i>Tugmalar orqali hisoblang yoki to'g'ridan-to'g'ri ifodani yozing!</i>"
    )


def extract_calc_expression(text: str) -> str:
    """Kalkulyator xabaridan joriy ifodani ajratib olish."""
    lines = text.split("━━━━━━━━━━━━━━━━━━━━")
    if len(lines) >= 3:
        expr = lines[1].strip()
        expr = expr.replace("<code>", "").replace("</code>", "").strip()
        return expr if expr else "0"
    return "0"


# ==========================================
# KOMANDALAR VA ASOSIY HANDLERLAR
# ==========================================

@dp.message(CommandStart())
async def cmd_start(message: Message):
    """/start komandasi uchun handler."""
    user_name = message.from_user.full_name if message.from_user else "Foydalanuvchi"
    welcome_text = (
        f"Assalomu alaykum, <b>{user_name}</b>! 👋\n\n"
        "Men <b>Aqlli Kalkulyator Botman</b> 🤖\n\n"
        "Men orqali 2 xil usulda hisob-kitob qilishingiz mumkin:\n"
        "1️⃣ <b>Matn yuborish:</b> Istalgan matematik ifodani to'g'ridan-to'g'ri yozib yuboring.\n"
        "   Masalan: <code>(25 + 75) * 4 / 2</code> yoki <code>sqrt(144) + 2^4</code>\n"
        "2️⃣ <b>Interaktiv kalkulyator:</b> Pastdagi <b>🧮 Kalkulyator</b> tugmasini bosing yoki /calc buyrug'ini yuboring!\n\n"
        "📌 Qo'llanma uchun: /help\n"
        "💡 Namunalar uchun: /examples"
    )
    await message.answer(
        welcome_text,
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_reply_keyboard()
    )


@dp.message(Command("help"))
@dp.message(F.text == "ℹ️ Yordam")
async def cmd_help(message: Message):
    """/help komandasi va 'ℹ️ Yordam' tugmasi uchun handler."""
    help_text = (
        "📖 <b>Botdan foydalanish bo'yicha mukammal qo'llanma</b>\n\n"
        "<b>Qo'llab-quvvatlanadigan asosiy amallar:</b>\n"
        "➕ <code>+</code> : Qo'shish (masalan: <code>15 + 25</code>)\n"
        "➖ <code>-</code> : Ayirish (masalan: <code>100 - 35</code>)\n"
        "✖️ <code>*</code> yoki <code>×</code>, <code>x</code> : Ko'paytirish (masalan: <code>6 * 7</code>, <code>10 x 5</code>)\n"
        "➗ <code>/</code> yoki <code>÷</code>, <code>:</code> : Bo'lish (masalan: <code>100 / 4</code>, <code>100 : 5</code>)\n"
        "🔢 <code>//</code> : Butunli bo'lish (masalan: <code>17 // 3</code> ➡️ 5)\n"
        "🔢 <code>%</code> : Qoldiqli bo'lish yoki Foiz (masalan: <code>200 * 15%</code> ➡️ 30)\n"
        "⚡️ <code>**</code> yoki <code>^</code> : Darajaga ko'tarish (masalan: <code>2^8</code> ➡️ 256)\n"
        "❗ <code>!</code> : Faktorial (masalan: <code>5!</code> ➡️ 120)\n"
        "괄 <code>( )</code> yoki <code>[ ]</code> : Qavslar (masalan: <code>(10 + 5) * 2</code>)\n\n"
        "<b>Matematik funksiyalar va doimiylar:</b>\n"
        "▫️ <code>sqrt(x)</code> yoki <code>√x</code> : Kvadrat ildiz (masalan: <code>sqrt(81)</code> ➡️ 9)\n"
        "▫️ <code>cbrt(x)</code> : Kub ildiz (masalan: <code>cbrt(27)</code> ➡️ 3)\n"
        "▫️ <code>abs(x)</code> : Modul / Absolyut qiymat (masalan: <code>abs(-25)</code> ➡️ 25)\n"
        "▫️ <code>sin(x)</code>, <code>cos(x)</code>, <code>tan(x)</code> : Trigonometriya (radianlarda)\n"
        "▫️ <code>sind(x)</code>, <code>cosd(x)</code>, <code>tand(x)</code> : Trigonometriya (graduslarda, masalan: <code>sind(90)</code> ➡️ 1)\n"
        "▫️ <code>log(x, base)</code>, <code>ln(x)</code>, <code>lg(x)</code> : Logarifmlar\n"
        "▫️ <code>gcd(a, b)</code> : EKUB (eng katta umumiy bo'luvchi)\n"
        "▫️ <code>lcm(a, b)</code> : EKUK (eng kichik umumiy karrali)\n"
        "▫️ <code>min(a, b)</code>, <code>max(a, b)</code> : Eng kichik / eng katta son\n"
        "▫️ <code>pi</code> (π), <code>e</code> : Matematik konstantalar\n\n"
        "💡 <i>Istalgan ifodani chatga yuboring, bot bir zumda hisoblab beradi!</i>"
    )
    await message.answer(
        help_text,
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_reply_keyboard()
    )


@dp.message(Command("examples"))
@dp.message(F.text == "💡 Misollar")
async def cmd_examples(message: Message):
    """Foydalanish namunalarini ko'rsatish."""
    examples_text = (
        "💡 <b>Kalkulyator uchun namunaviy ifodalar:</b>\n\n"
        "1️⃣ <b>Oddiy hisob-kitoblar:</b>\n"
        "▫️ <code>(250 + 750) / 4</code>\n"
        "▫️ <code>15.5 * 4 - 12.3</code>\n"
        "▫️ <code>2,5 + 3,5 * 2</code>\n\n"
        "2️⃣ <b>Darajalar va ildizlar:</b>\n"
        "▫️ <code>2^10 + 5^3</code>\n"
        "▫️ <code>sqrt(225) + √100</code>\n"
        "▫️ <code>cbrt(125)</code>\n\n"
        "3️⃣ <b>Foiz va faktorial:</b>\n"
        "▫️ <code>500 * 20%</code>\n"
        "▫️ <code>6! + 4!</code>\n\n"
        "4️⃣ <b>Funksiyalar va doimiylar:</b>\n"
        "▫️ <code>2pi * 5</code>\n"
        "▫️ <code>sind(90) + cosd(0)</code>\n"
        "▫️ <code>gcd(48, 64)</code>\n"
        "▫️ <code>log(1000, 10)</code>\n\n"
        "<i>Biron bir ifodani nusxalab yuborib ko'ring!</i> 🚀"
    )
    await message.answer(
        examples_text,
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_reply_keyboard()
    )


@dp.message(Command("calc"))
@dp.message(F.text == "🧮 Kalkulyator")
async def cmd_calculator(message: Message):
    """Interaktiv inline kalkulyatorni ochish."""
    await message.answer(
        format_calc_screen("0"),
        parse_mode=ParseMode.HTML,
        reply_markup=get_calculator_keyboard()
    )


# ==========================================
# INLINE KALKULYATOR TUGMALARI (CALLBACKS)
# ==========================================

@dp.callback_query(F.data.startswith("calc:"))
async def handle_calculator_callback(callback: CallbackQuery):
    """Inline kalkulyator tugmalari bosilganda ishlovchi funksiya."""
    action = callback.data.split(":", 1)[1]
    current_text = callback.message.text or ""
    current_expr = extract_calc_expression(current_text)

    new_expr = current_expr

    if action == "close":
        try:
            await callback.message.edit_text(
                "❌ <b>Kalkulyator yopildi.</b>\nQayta ochish uchun pastdagi <b>🧮 Kalkulyator</b> tugmasini bosing yoki /calc buyrug'ini bering.",
                parse_mode=ParseMode.HTML,
                reply_markup=None
            )
        except TelegramBadRequest:
            pass
        await callback.answer()
        return

    elif action == "clear":
        new_expr = "0"

    elif action == "back":
        if current_expr in ("0", "❌ Xato") or "Xatolik" in current_expr or len(current_expr) <= 1:
            new_expr = "0"
        else:
            # Agar oxirida 'sqrt(' bo'lsa, butun 'sqrt(' ni o'chirish
            if new_expr.endswith("sqrt("):
                new_expr = new_expr[:-5]
            elif new_expr.endswith("**"):
                new_expr = new_expr[:-2]
            else:
                new_expr = new_expr[:-1].strip()
            
            if not new_expr:
                new_expr = "0"

    elif action == "neg":
        # Ishorani o'zgartirish (+/-)
        if current_expr in ("0", "❌ Xato") or "Xatolik" in current_expr:
            new_expr = "-"
        elif current_expr.startswith("-(") and current_expr.endswith(")"):
            new_expr = current_expr[2:-1]
        elif current_expr.startswith("-"):
            new_expr = current_expr[1:]
        elif any(op in current_expr for op in ("+", "-", "*", "/", "%", "^")):
            new_expr = f"-({current_expr})"
        else:
            new_expr = f"-{current_expr}"

    elif action == "eval":
        if current_expr in ("0", "❌ Xato") or "Xatolik" in current_expr:
            await callback.answer("Avval ifodani kiriting!", show_alert=False)
            return

        success, result = evaluate_math(current_expr)
        if success:
            new_expr = f"{result}"
            await callback.answer(f"Natija: {result}")
        else:
            new_expr = "0"
            await callback.answer(result, show_alert=True)

    else:
        # Raqam yoki operator kiritilganda
        token = action
        is_reset_state = current_expr in ("0", "❌ Xato") or "Xatolik" in current_expr

        if is_reset_state:
            if token in ("+", "*", "/", "%", "**"):
                new_expr = f"0{token}"
            elif token == "sqrt(":
                new_expr = "sqrt("
            else:
                new_expr = token
        else:
            # Ketma-ket keraksiz operatorlar qo'shilishining oldini olish
            operators = ("+", "-", "*", "/", "%", "**")
            if token in operators and any(current_expr.endswith(op) for op in operators):
                # Oxirgi operatorni yangisiga almashtirish
                for op in ("**", "+", "-", "*", "/", "%"):
                    if current_expr.endswith(op):
                        new_expr = current_expr[:-len(op)] + token
                        break
            else:
                new_expr = f"{current_expr}{token}"

    # Agar ifoda o'zgarmagan bo'lsa qayta tahrirlamaslik
    new_message_text = format_calc_screen(new_expr)
    try:
        await callback.message.edit_text(
            new_message_text,
            parse_mode=ParseMode.HTML,
            reply_markup=get_calculator_keyboard()
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e).lower():
            logger.warning(f"Xabarni yangilashda ogohlantirish: {e}")

    try:
        await callback.answer()
    except Exception:
        pass


# ==========================================
# MATNLI MATEMATIK IFODALARNI HISOB-KITOB QILISH
# ==========================================

def looks_like_math_expression(text: str) -> bool:
    """Matn matematik ifodaga o'xshashligini tekshirish."""
    if not text or not text.strip():
        return False

    clean = text.strip().lower()
    
    # Oxiridagi '=' va '?' belgilarini tozalash
    clean = re.sub(r'[\s=\?]+$', '', clean).strip()
    if not clean:
        return False

    # Barcha ruxsat etilgan funksiya va konstantalar ro'yxati
    all_math_words = set(CONSTANTS.keys()) | set(MATH_FUNCTIONS.keys()) | {"pi", "e", "tau", "inf"}
    
    # So'zlarni olib tashlash
    for kw in sorted(all_math_words, key=len, reverse=True):
        clean = re.sub(rf'\b{kw}\b', '', clean)

    # Ruxsat etilgan belgilar: raqamlar, amallar, qavslar, x, X, :, vergul va nuqta
    math_chars = set("0123456789+-*/÷×✕·:^%!()[]{}., π√ xX")
    
    # Qolgan barcha belgilar matematik belgilar to'plamida bormi?
    is_valid_chars = all(c in math_chars for c in clean)
    
    # Agar faqat bo'shliqlar qolgan bo'lsa va matnda kamida bitta matematik belgi yoki raqam bo'lsa
    has_math_component = any(c.isdigit() for c in text) or any(c in "+-*/÷×:^%!√π" for c in text) or any(kw in text.lower() for kw in all_math_words)
    
    return is_valid_chars and has_math_component


@dp.message(F.text)
async def handle_math_message(message: Message):
    """Foydalanuvchi yuborgan ixtiyoriy matnli matematik ifodani hisoblash."""
    user_input = message.text.strip()

    # Agar foydalanuvchi shunchaki oddiy matn (salom, qalay va h.k.) yozsa
    if not looks_like_math_expression(user_input):
        await message.answer(
            "🤔 <b>Men faqat matematik ifodalarni hisoblay olaman!</b>\n\n"
            "Misollar:\n"
            "▫️ <code>(150 + 250) * 2</code>\n"
            "▫️ <code>15^2 + sqrt(144)</code>\n"
            "▫️ <code>12.5 * 4 - 10 / 2</code>\n"
            "▫️ <code>500 * 15%</code>\n"
            "▫️ <code>5! + sind(90)</code>\n\n"
            "Yoki interaktiv kalkulyatordan foydalanish uchun <b>🧮 Kalkulyator</b> tugmasini bosing!",
            parse_mode=ParseMode.HTML
        )
        return

    # Matematik ifodani hisoblash
    success, result = evaluate_math(user_input)

    if success:
        response_text = (
            "🧮 <b>Hisoblash natijasi:</b>\n\n"
            f"📝 <b>Ifoda:</b> <code>{user_input}</code>\n"
            f"✅ <b>Natija:</b> <code>{result}</code>"
        )
        await message.reply(
            response_text,
            parse_mode=ParseMode.HTML
        )
    else:
        # Xatolik haqida xabar berish
        await message.reply(
            f"{result}\n\n💡 Ifodani to'g'ri yozishga misol: <code>(20 + 5) * 4</code> yoki <code>sqrt(144) + 5^2</code>",
            parse_mode=ParseMode.HTML
        )


# ==========================================
# ASOSIY ISHGA TUSHIRISH FUNKSIYASI
# ==========================================

async def main():
    """Botni ishga tushirish."""
    if not BOT_TOKEN or BOT_TOKEN == "SIZNING_BOT_TOKENINGIZ":
        logger.error(
            "XATOLIK: BOT_TOKEN topilmadi!\n"
            "Iltimos, .env faylini tekshiring va Telegram @BotFather'dan olgan tokeningizni kiriting."
        )
        print("\n" + "="*60)
        print("❌ DIQQAT: BOT_TOKEN o'rnatilmagan!")
        print("1. .env fayliga bot tokeningizni yozing:")
        print("   BOT_TOKEN=8776105818:AAGefFpLY98E7_MkomKccesYcS51xEJyC5U")
        print("2. Qayta ishga tushiring: python bot.py")
        print("="*60 + "\n")
        return

    # Bot obyekti yaratish
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # Bot menyusi komandalarini o'rnatish
    await bot.set_my_commands([
        BotCommand(command="start", description="Botni qayta ishga tushirish"),
        BotCommand(command="calc", description="Interaktiv kalkulyatorni ochish"),
        BotCommand(command="help", description="Qo'llanma va barcha amallar"),
        BotCommand(command="examples", description="Namunaviy misollar"),
    ])

    logger.info("Bot muvaffaqiyatli ishga tushdi va xabarlarni kutmoqda...")
    print("\n🚀 Bot ishga tushdi! Telegram orqali /start buyrug'ini yuboring.\n")

    # Polling rejimida xabarlarni qabul qilish
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
