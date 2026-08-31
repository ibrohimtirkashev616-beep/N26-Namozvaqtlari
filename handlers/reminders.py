# -*- coding: utf-8 -*-
"""
Eslatmalarni sozlash va daqiqalar tanlovi (3 tilda)
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode
import config
import database
from texts import get_text, TEXTS
import keyboards

router = Router()


@router.message(F.text.in_([
    "🔔 Eslatma sozlamalari",
    "🔔 Настройки напоминаний",
    "🔔 Reminder settings"
]))
async def handle_reminders_btn(message: Message):
    """Eslatma sozlamalari reply tugmasi."""
    user = await database.get_user(message.from_user.id)
    if not user:
        user = await database.create_or_update_user(message.from_user.id)
        
    lang = user.get("language", "uz")
    reminders = user.get("reminders", config.DEFAULT_REMINDERS.copy())
    reminder_before = user.get("reminder_before", 0)
    
    cur_before_text = TEXTS["reminder_options"].get(lang, TEXTS["reminder_options"]["uz"]).get(reminder_before, f"{reminder_before} min")
    text = get_text("reminders_menu", lang, current_before=cur_before_text)
    kb = keyboards.get_reminders_keyboard(reminders, reminder_before, lang)
    
    await message.answer(text, reply_markup=kb, parse_mode=ParseMode.HTML)


@router.callback_query(F.data.startswith("rem_toggle:"))
async def cb_toggle_reminder(callback: CallbackQuery):
    """Namoz eslatmasini yoqish/o'chirish toggle."""
    prayer_name = callback.data.split(":")[1]
    user_id = callback.from_user.id
    
    new_reminders = await database.toggle_prayer_reminder(user_id, prayer_name)
    user = await database.get_user(user_id)
    lang = user.get("language", "uz") if user else "uz"
    reminder_before = user.get("reminder_before", 0) if user else 0
    
    cur_before_text = TEXTS["reminder_options"].get(lang, TEXTS["reminder_options"]["uz"]).get(reminder_before, f"{reminder_before} min")
    text = get_text("reminders_menu", lang, current_before=cur_before_text)
    kb = keyboards.get_reminders_keyboard(new_reminders, reminder_before, lang)
    
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.HTML)
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data == "rem_open_time")
async def cb_open_reminder_time(callback: CallbackQuery):
    """Necha daqiqa oldin menyusini ochish."""
    user = await database.get_user(callback.from_user.id)
    lang = user.get("language", "uz") if user else "uz"
    reminder_before = user.get("reminder_before", 0) if user else 0
    
    text = get_text("choose_reminder_time", lang)
    kb = keyboards.get_reminder_time_keyboard(reminder_before, lang)
    
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.HTML)
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data.startswith("rem_set_time:"))
async def cb_set_reminder_time(callback: CallbackQuery):
    """Daqiqani tanlash va asosiy eslatma menyusiga qaytish."""
    minutes = int(callback.data.split(":")[1])
    user_id = callback.from_user.id
    
    await database.set_reminder_before(user_id, minutes)
    user = await database.get_user(user_id)
    lang = user.get("language", "uz") if user else "uz"
    reminders = user.get("reminders", config.DEFAULT_REMINDERS.copy()) if user else config.DEFAULT_REMINDERS.copy()
    
    cur_before_text = TEXTS["reminder_options"].get(lang, TEXTS["reminder_options"]["uz"]).get(minutes, f"{minutes} min")
    text = get_text("reminders_menu", lang, current_before=cur_before_text)
    kb = keyboards.get_reminders_keyboard(reminders, minutes, lang)
    
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.HTML)
    except Exception:
        pass
    
    saved_alert = {"uz": "✅ Saqlandi", "ru": "✅ Сохранено", "en": "✅ Saved"}
    await callback.answer(saved_alert.get(lang, "✅ Saved"))


@router.callback_query(F.data == "rem_back")
async def cb_rem_back(callback: CallbackQuery):
    """Eslatma menyusiga qaytish."""
    user = await database.get_user(callback.from_user.id)
    lang = user.get("language", "uz") if user else "uz"
    reminders = user.get("reminders", config.DEFAULT_REMINDERS.copy()) if user else config.DEFAULT_REMINDERS.copy()
    reminder_before = user.get("reminder_before", 0) if user else 0
    
    cur_before_text = TEXTS["reminder_options"].get(lang, TEXTS["reminder_options"]["uz"]).get(reminder_before, f"{reminder_before} min")
    text = get_text("reminders_menu", lang, current_before=cur_before_text)
    kb = keyboards.get_reminders_keyboard(reminders, reminder_before, lang)
    
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.HTML)
    except Exception:
        pass
    await callback.answer()
