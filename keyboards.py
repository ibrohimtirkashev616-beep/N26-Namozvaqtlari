# -*- coding: utf-8 -*-
"""
Inline va Reply klaviaturalar (O'zbek, Rus, Ingliz tillari va 12 viloyat)
"""

from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)
import config
from texts import (
    get_text,
    PRAYER_NAMES,
    TEXTS
)


def get_language_inline_keyboard() -> InlineKeyboardMarkup:
    """Til tanlash tugmalari (O'zbek, Rus, Ingliz)."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇿 O'zbek tili", callback_data="set_lang:uz"),
                InlineKeyboardButton(text="🇷🇺 Русский язык", callback_data="set_lang:ru")
            ],
            [
                InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang:en")
            ]
        ]
    )


def get_region_inline_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    """O'zbekistonning barcha viloyat markazlari tugmalari (2 ustunli tartibda)."""
    buttons = []
    for r_code, r_info in config.REGIONS.items():
        btn_text = r_info.get(f"button_{lang}") or r_info.get("button_uz")
        buttons.append(
            InlineKeyboardButton(text=btn_text, callback_data=f"set_region:{r_code}")
        )
    
    # 2 tadan guruhlash
    rows = []
    for i in range(0, len(buttons), 2):
        rows.append(buttons[i:i+2])
        
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_main_reply_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Asosiy 4 ta doimiy bo'lim tugmalari (Reply Keyboard)."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=get_text("btn_today", lang)),
                KeyboardButton(text=get_text("btn_week", lang))
            ],
            [
                KeyboardButton(text=get_text("btn_reminders", lang)),
                KeyboardButton(text=get_text("btn_settings", lang))
            ]
        ],
        resize_keyboard=True,
        persistent=True
    )


def get_today_inline_keyboard(lang: str = "uz", is_tomorrow: bool = False) -> InlineKeyboardMarkup:
    """Bugungi/ertangi kun namoz vaqtlari ostidagi tugmalar."""
    refresh_btn = InlineKeyboardButton(
        text=get_text("btn_refresh", lang),
        callback_data="today_refresh"
    )
    if is_tomorrow:
        toggle_day_btn = InlineKeyboardButton(
            text=get_text("btn_today_inline", lang),
            callback_data="today_show_today"
        )
    else:
        toggle_day_btn = InlineKeyboardButton(
            text=get_text("btn_tomorrow", lang),
            callback_data="today_show_tomorrow"
        )
        
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [refresh_btn, toggle_day_btn]
        ]
    )


def get_weekly_nav_keyboard(lang: str = "uz", week_offset: int = 0) -> InlineKeyboardMarkup:
    """Haftalik jadval navigatsiya tugmalari."""
    prev_offset = week_offset - 1
    next_offset = week_offset + 1
    
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=get_text("btn_prev_week", lang), callback_data=f"week_nav:{prev_offset}"),
                InlineKeyboardButton(text=get_text("btn_next_week", lang), callback_data=f"week_nav:{next_offset}")
            ]
        ]
    )


def get_reminders_keyboard(reminders: dict, reminder_before: int, lang: str = "uz") -> InlineKeyboardMarkup:
    """Eslatmalarni boshqarish tugmalari (✅/❌ toggle)."""
    rows = []
    
    for p_key in config.PRAYER_KEYS:
        is_on = reminders.get(p_key, True)
        icon = "✅" if is_on else "❌"
        p_name = PRAYER_NAMES.get(lang, {}).get(p_key, p_key)
        btn_text = f"{icon} {p_name}"
        rows.append([
            InlineKeyboardButton(text=btn_text, callback_data=f"rem_toggle:{p_key}")
        ])
        
    opt_text = TEXTS["reminder_options"].get(lang, TEXTS["reminder_options"]["uz"]).get(reminder_before, f"{reminder_before} min")
    how_many_btn_text = f"⏱ {get_text('btn_how_many_minutes', lang)} ({opt_text})"
    rows.append([
        InlineKeyboardButton(text=how_many_btn_text, callback_data="rem_open_time")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_reminder_time_keyboard(current_before: int, lang: str = "uz") -> InlineKeyboardMarkup:
    """Necha daqiqa oldin eslatish vaqtini tanlash."""
    buttons = []
    for opt in config.REMINDER_BEFORE_OPTIONS:
        text = TEXTS["reminder_options"].get(lang, TEXTS["reminder_options"]["uz"]).get(opt, f"{opt} min")
        prefix = "✅ " if opt == current_before else ""
        buttons.append(
            InlineKeyboardButton(text=f"{prefix}{text}", callback_data=f"rem_set_time:{opt}")
        )
        
    rows = [
        [buttons[0], buttons[1]],
        [buttons[2], buttons[3]],
        [InlineKeyboardButton(text=get_text("btn_back", lang), callback_data="rem_back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_settings_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    """Sozlamalar menyusi inline tugmalari."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=get_text("btn_change_region", lang), callback_data="settings_region")],
            [InlineKeyboardButton(text=get_text("btn_change_lang", lang), callback_data="settings_lang")],
            [InlineKeyboardButton(text=get_text("btn_manage_reminders", lang), callback_data="settings_reminders")]
        ]
    )
