"""
Foydalanuvchi uchun Reply klaviaturalari
"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Asosiy menyu klaviaturasi."""
    kb = [
        [
            KeyboardButton(text="📝 Ariza topshirish"),
            KeyboardButton(text="⚡ Tezkor CV tahlili")
        ],
        [
            KeyboardButton(text="💼 Bo'sh ish o'rinlari"),
            KeyboardButton(text="📊 Mening arizalarim")
        ],
        [
            KeyboardButton(text="ℹ️ Bot haqida / Yordam")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=False)


def get_phone_request_keyboard() -> ReplyKeyboardMarkup:
    """Telefon raqamni yuborish klaviaturasi."""
    kb = [
        [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)],
        [KeyboardButton(text="❌ Bekor qilish")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Faqat bekor qilish klaviaturasi."""
    kb = [
        [KeyboardButton(text="❌ Bekor qilish")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def get_skip_or_cancel_keyboard() -> ReplyKeyboardMarkup:
    """O'tkazib yuborish yoki bekor qilish."""
    kb = [
        [KeyboardButton(text="⏭ O'tkazib yuborish")],
        [KeyboardButton(text="❌ Bekor qilish")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
