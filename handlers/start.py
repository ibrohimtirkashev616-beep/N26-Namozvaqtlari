# -*- coding: utf-8 -*-
"""
/start, /help, Til va Hudud tanlash handlerlari (3 til va 12 viloyat)
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
import config
import database
import prayer_api
from texts import get_text
import keyboards

router = Router()


@router.message(CommandStart())
async def handle_start(message: Message):
    """/start komandasi."""
    user_id = message.from_user.id
    user = await database.get_user(user_id)
    
    if not user:
        text = get_text("start_welcome", "uz")
        kb = keyboards.get_language_inline_keyboard()
        await message.answer(text, reply_markup=kb, parse_mode=ParseMode.HTML)
    else:
        lang = user.get("language", "uz")
        region_code = user.get("region", "tashkent")
        reg_info = config.REGIONS.get(region_code, config.REGIONS["tashkent"])
        
        reply_kb = keyboards.get_main_reply_keyboard(lang)
        today = prayer_api.get_current_datetime().date()
        sana, hafta_kuni = prayer_api.format_date_title(today, lang)
        
        timings = await prayer_api.get_timings(region_code, today)
        if timings:
            next_name, next_time, time_left = prayer_api.calculate_next_prayer(timings, lang)
            hudud_name = reg_info.get(f"name_{lang}") or reg_info.get("name_uz")
            today_text = get_text(
                "today_template",
                lang,
                hudud=hudud_name,
                sana=sana,
                hafta_kuni=hafta_kuni,
                fajr=timings.get("fajr", "--:--"),
                sunrise=timings.get("sunrise", "--:--"),
                dhuhr=timings.get("dhuhr", "--:--"),
                asr=timings.get("asr", "--:--"),
                maghrib=timings.get("maghrib", "--:--"),
                isha=timings.get("isha", "--:--"),
                next_name=next_name,
                next_time=next_time,
                time_left=time_left
            )
            inline_kb = keyboards.get_today_inline_keyboard(lang, is_tomorrow=False)
            await message.answer("🕌", reply_markup=reply_kb)
            await message.answer(today_text, reply_markup=inline_kb, parse_mode=ParseMode.HTML)
        else:
            await message.answer(get_text("error_loading", lang), reply_markup=reply_kb, parse_mode=ParseMode.HTML)


@router.message(Command("help"))
async def handle_help(message: Message):
    """/help komandasi."""
    user = await database.get_user(message.from_user.id)
    lang = user.get("language", "uz") if user else "uz"
    
    if lang == "ru":
        help_text = (
            "📖 <b>Помощь по боту:</b>\n\n"
            "Этот бот показывает точное время намаза для всех регионов Узбекистана и вовремя присылает напоминания.\n\n"
            "Пожалуйста, воспользуйтесь кнопками меню внизу для быстрого доступа."
        )
    elif lang == "en":
        help_text = (
            "📖 <b>Bot Help:</b>\n\n"
            "This bot provides accurate prayer times for all regions of Uzbekistan and sends timely reminders.\n\n"
            "Please use the menu buttons below for easy access."
        )
    else:
        help_text = (
            "📖 <b>Bot haqida yordam:</b>\n\n"
            "Ushbu bot O'zbekistonning barcha hududlari uchun aniq namoz vaqtlarini ko'rsatadi va o'z vaqtida azon/eslatma yuboradi.\n\n"
            "Pastdagi qulay menyu tugmalaridan foydalanishingiz mumkin."
        )
    await message.answer(help_text, parse_mode=ParseMode.HTML)


@router.callback_query(F.data.startswith("set_lang:"))
async def cb_set_language(callback: CallbackQuery):
    """Til tanlanganda hudud tanlashga o'tish."""
    lang = callback.data.split(":")[1]
    user_id = callback.from_user.id
    
    await database.create_or_update_user(user_id, language=lang)
    
    text = get_text("choose_region", lang)
    kb = keyboards.get_region_inline_keyboard(lang)
    
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.HTML)
    except Exception:
        await callback.message.answer(text, reply_markup=kb, parse_mode=ParseMode.HTML)
    await callback.answer()


@router.callback_query(F.data.startswith("set_region:"))
async def cb_set_region(callback: CallbackQuery):
    """Hudud tanlanganda ro'yxatdan o'tishni yakunlash."""
    region_code = callback.data.split(":")[1]
    user_id = callback.from_user.id
    
    user = await database.get_user(user_id)
    lang = user.get("language", "uz") if user else "uz"
    
    await database.create_or_update_user(user_id, region=region_code)
    reg_info = config.REGIONS.get(region_code, config.REGIONS["tashkent"])
    
    lang_map = {"uz": "O'zbek tili", "ru": "Русский язык", "en": "English"}
    lang_display = lang_map.get(lang, "O'zbek tili")
    reg_display = reg_info.get(f"name_{lang}") or reg_info.get("name_uz")
    
    confirm_text = get_text("reg_success", lang, region=reg_display, language=lang_display)
    reply_kb = keyboards.get_main_reply_keyboard(lang)
    
    try:
        await callback.message.delete()
    except Exception:
        pass
        
    await callback.message.answer(confirm_text, reply_markup=reply_kb, parse_mode=ParseMode.HTML)
    
    today = prayer_api.get_current_datetime().date()
    sana, hafta_kuni = prayer_api.format_date_title(today, lang)
    timings = await prayer_api.get_timings(region_code, today)
    
    if timings:
        next_name, next_time, time_left = prayer_api.calculate_next_prayer(timings, lang)
        today_text = get_text(
            "today_template",
            lang,
            hudud=reg_display,
            sana=sana,
            hafta_kuni=hafta_kuni,
            fajr=timings.get("fajr", "--:--"),
            sunrise=timings.get("sunrise", "--:--"),
            dhuhr=timings.get("dhuhr", "--:--"),
            asr=timings.get("asr", "--:--"),
            maghrib=timings.get("maghrib", "--:--"),
            isha=timings.get("isha", "--:--"),
            next_name=next_name,
            next_time=next_time,
            time_left=time_left
        )
        inline_kb = keyboards.get_today_inline_keyboard(lang, is_tomorrow=False)
        await callback.message.answer(today_text, reply_markup=inline_kb, parse_mode=ParseMode.HTML)
    await callback.answer()
