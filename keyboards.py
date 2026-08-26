"""
Telegram bot uchun klaviatura (Keyboards) moduli.
Inline kalkulyator tugmalari va asosiy menyu tugmalarini o'z ichiga oladi.
"""

from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def get_calculator_keyboard() -> InlineKeyboardMarkup:
    """Interaktiv inline kalkulyator klaviaturasini yaratadi."""
    builder = InlineKeyboardBuilder()

    buttons = [
        # 1-qator: Tozalash, O'chirish, Qavslar
        [("C", "calc:clear"), ("⌫", "calc:back"), ("(", "calc:("), (")", "calc:)")],
        # 2-qator: Ildiz, Daraja, Foiz, Bo'lish
        [("√", "calc:sqrt("), ("^", "calc:**"), ("%", "calc:%"), ("÷", "calc:/")],
        # 3-qator: 7, 8, 9, Ko'paytirish
        [("7", "calc:7"), ("8", "calc:8"), ("9", "calc:9"), ("×", "calc:*")],
        # 4-qator: 4, 5, 6, Ayirish
        [("4", "calc:4"), ("5", "calc:5"), ("6", "calc:6"), ("-", "calc:-")],
        # 5-qator: 1, 2, 3, Qo'shish
        [("1", "calc:1"), ("2", "calc:2"), ("3", "calc:3"), ("+", "calc:+")],
        # 6-qator: Ishora, 0, Nuqta, Barobar
        [("±", "calc:neg"), ("0", "calc:0"), (".", "calc:."), ("=", "calc:eval")],
        # 7-qator: Yopish
        [("❌ Kalkulyatorni yopish", "calc:close")],
    ]

    for row in buttons:
        builder.row(*[
            InlineKeyboardButton(text=text, callback_data=data)
            for text, data in row
        ])

    return builder.as_markup()


def get_main_reply_keyboard() -> ReplyKeyboardMarkup:
    """Asosiy pastki menyu klaviaturasi."""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="🧮 Kalkulyator"),
        KeyboardButton(text="ℹ️ Yordam"),
    )
    builder.row(
        KeyboardButton(text="💡 Misollar")
    )
    return builder.as_markup(resize_keyboard=True)
