"""
Inline klaviaturalar
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Dict, Any
import config

def get_vacancies_inline_keyboard() -> InlineKeyboardMarkup:
    """Mavjud vakansiyalar ro'yxati klaviaturasi."""
    buttons = []
    for key, val in config.VACANCIES.items():
        buttons.append([InlineKeyboardButton(text=val["title"], callback_data=f"apply_vac:{key}")])
    
    buttons.append([InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_application")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_vacancy_info_keyboard() -> InlineKeyboardMarkup:
    """Vakansiyalar haqida ma'lumot olish klaviaturasi."""
    buttons = []
    for key, val in config.VACANCIES.items():
        buttons.append([InlineKeyboardButton(text=val["title"], callback_data=f"info_vac:{key}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_application_confirm_keyboard() -> InlineKeyboardMarkup:
    """Arizani tasdiqlash klaviaturasi."""
    buttons = [
        [
            InlineKeyboardButton(text="🚀 Tasdiqlash va Yuborish", callback_data="submit_app_confirm"),
        ],
        [
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_application")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_hr_group_actions_keyboard(app_id: int) -> InlineKeyboardMarkup:
    """HR guruhi uchun nomzod ustidan amallar klaviaturasi."""
    buttons = [
        [
            InlineKeyboardButton(text="✅ Suhbatga chaqirish", callback_data=f"hr_act:invite:{app_id}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"hr_act:reject:{app_id}")
        ],
        [
            InlineKeyboardButton(text="⭐ Zaxiraga olish", callback_data=f"hr_act:reserve:{app_id}"),
            InlineKeyboardButton(text="💬 Xabar yuborish", callback_data=f"hr_act:msg:{app_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_quick_cv_vacancy_keyboard() -> InlineKeyboardMarkup:
    """Tezkor CV tahlili uchun vakansiya tanlash."""
    buttons = []
    for key, val in config.VACANCIES.items():
        buttons.append([InlineKeyboardButton(text=val["title"], callback_data=f"quick_vac:{key}")])
    buttons.append([InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_application")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
