# -*- coding: utf-8 -*-
"""
Sozlamalar bo'limi (Hudud, Til, Eslatmalarni o'zgartirish)
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode
import config
import database
from texts import get_text
import keyboards

router = Router()


@router.message(F.text.in_([
    "⚙️ Sozlamalar",
    "⚙️ Настройки",
    "⚙️ Settings"
]))
async def handle_settings_btn(message: Message):
    """Sozlamalar reply tugmasi."""
    user = await database.get_user(message.from_user.id)
    if not user:
        user = await database.create_or_update_user(message.from_user.id)
        
    lang = user.get("language", "uz")
    region_code = user.get("region", "tashkent")
    reg_info = config.REGIONS.get(region_code, config.REGIONS["tashkent"])
    
    lang_names = {"uz": "O'zbek tili", "ru": "Русский язык", "en": "English"}
    lang_display = lang_names.get(lang, "O'zbek tili")
    hudud_display = reg_info.get(f"name_{lang}") or reg_info.get("name_uz")
    
    text = get_text("settings_menu", lang, hudud=hudud_display, til=lang_display)
    kb = keyboards.get_settings_keyboard(lang)
    
    await message.answer(text, reply_markup=kb, parse_mode=ParseMode.HTML)


@router.callback_query(F.data == "settings_region")
async def cb_settings_change_region(callback: CallbackQuery):
    """Sozlamalardan hududni o'zgartirish."""
    user = await database.get_user(callback.from_user.id)
    lang = user.get("language", "uz") if user else "uz"
    
    text = get_text("choose_region", lang)
    kb = keyboards.get_region_inline_keyboard(lang)
    
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.HTML)
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data == "settings_lang")
async def cb_settings_change_lang(callback: CallbackQuery):
    """Sozlamalardan tilni o'zgartirish."""
    text = get_text("start_welcome", "uz")
    kb = keyboards.get_language_inline_keyboard()
    
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.HTML)
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data == "settings_reminders")
async def cb_settings_reminders(callback: CallbackQuery):
    """Sozlamalardan eslatmalarga o'tish."""
    user = await database.get_user(callback.from_user.id)
    lang = user.get("language", "uz") if user else "uz"
    reminders = user.get("reminders", config.DEFAULT_REMINDERS.copy()) if user else config.DEFAULT_REMINDERS.copy()
    reminder_before = user.get("reminder_before", 0) if user else 0
    
    from texts import TEXTS
    cur_before_text = TEXTS["reminder_options"].get(lang, TEXTS["reminder_options"]["uz"]).get(reminder_before, f"{reminder_before} min")
    text = get_text("reminders_menu", lang, current_before=cur_before_text)
    kb = keyboards.get_reminders_keyboard(reminders, reminder_before, lang)
    
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.HTML)
    except Exception:
        pass
    await callback.answer()
