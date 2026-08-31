# -*- coding: utf-8 -*-
"""
Bugungi va ertangi namoz vaqtlari, haftalik jadval (3 til va 12 viloyat)
"""

import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode
import config
import database
import prayer_api
from texts import get_text
import keyboards

router = Router()


@router.message(F.text.in_([
    "🕌 Bugungi namoz vaqtlari",
    "🕌 Время намаза на сегодня",
    "🕌 Today's prayer times"
]))
async def handle_today_prayer_btn(message: Message):
    """Bugungi namoz vaqtlari tugmasi."""
    user = await database.get_user(message.from_user.id)
    lang = user.get("language", "uz") if user else "uz"
    region_code = user.get("region", "tashkent") if user else "tashkent"
    reg_info = config.REGIONS.get(region_code, config.REGIONS["tashkent"])
    
    today = prayer_api.get_current_datetime().date()
    sana, hafta_kuni = prayer_api.format_date_title(today, lang)
    timings = await prayer_api.get_timings(region_code, today)
    
    if not timings:
        await message.answer(get_text("error_loading", lang), parse_mode=ParseMode.HTML)
        return
        
    next_name, next_time, time_left = prayer_api.calculate_next_prayer(timings, lang)
    hudud_name = reg_info.get(f"name_{lang}") or reg_info.get("name_uz")
    text = get_text(
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
    await message.answer(text, reply_markup=inline_kb, parse_mode=ParseMode.HTML)


@router.callback_query(F.data == "today_refresh")
async def cb_today_refresh(callback: CallbackQuery):
    """Bugungi vaqtlarni yangilash."""
    user = await database.get_user(callback.from_user.id)
    lang = user.get("language", "uz") if user else "uz"
    region_code = user.get("region", "tashkent") if user else "tashkent"
    reg_info = config.REGIONS.get(region_code, config.REGIONS["tashkent"])
    
    today = prayer_api.get_current_datetime().date()
    sana, hafta_kuni = prayer_api.format_date_title(today, lang)
    timings = await prayer_api.get_timings(region_code, today)
    
    if timings:
        next_name, next_time, time_left = prayer_api.calculate_next_prayer(timings, lang)
        hudud_name = reg_info.get(f"name_{lang}") or reg_info.get("name_uz")
        text = get_text(
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
        try:
            await callback.message.edit_text(text, reply_markup=inline_kb, parse_mode=ParseMode.HTML)
        except Exception:
            pass
    
    alert_msg = {"uz": "✅ Yangilandi", "ru": "✅ Обновлено", "en": "✅ Updated"}
    await callback.answer(alert_msg.get(lang, "✅ Updated"))


@router.callback_query(F.data == "today_show_tomorrow")
async def cb_today_show_tomorrow(callback: CallbackQuery):
    """Ertangi kun vaqtlarini ko'rsatish."""
    user = await database.get_user(callback.from_user.id)
    lang = user.get("language", "uz") if user else "uz"
    region_code = user.get("region", "tashkent") if user else "tashkent"
    reg_info = config.REGIONS.get(region_code, config.REGIONS["tashkent"])
    
    tomorrow = prayer_api.get_current_datetime().date() + datetime.timedelta(days=1)
    sana, hafta_kuni = prayer_api.format_date_title(tomorrow, lang)
    timings = await prayer_api.get_timings(region_code, tomorrow)
    
    if timings:
        hudud_name = reg_info.get(f"name_{lang}") or reg_info.get("name_uz")
        text = get_text(
            "tomorrow_template",
            lang,
            hudud=hudud_name,
            sana=sana,
            hafta_kuni=hafta_kuni,
            fajr=timings.get("fajr", "--:--"),
            sunrise=timings.get("sunrise", "--:--"),
            dhuhr=timings.get("dhuhr", "--:--"),
            asr=timings.get("asr", "--:--"),
            maghrib=timings.get("maghrib", "--:--"),
            isha=timings.get("isha", "--:--")
        )
        inline_kb = keyboards.get_today_inline_keyboard(lang, is_tomorrow=True)
        try:
            await callback.message.edit_text(text, reply_markup=inline_kb, parse_mode=ParseMode.HTML)
        except Exception:
            pass
    await callback.answer()


@router.callback_query(F.data == "today_show_today")
async def cb_today_show_today(callback: CallbackQuery):
    """Bugungi kunga qaytish."""
    user = await database.get_user(callback.from_user.id)
    lang = user.get("language", "uz") if user else "uz"
    region_code = user.get("region", "tashkent") if user else "tashkent"
    reg_info = config.REGIONS.get(region_code, config.REGIONS["tashkent"])
    
    today = prayer_api.get_current_datetime().date()
    sana, hafta_kuni = prayer_api.format_date_title(today, lang)
    timings = await prayer_api.get_timings(region_code, today)
    
    if timings:
        next_name, next_time, time_left = prayer_api.calculate_next_prayer(timings, lang)
        hudud_name = reg_info.get(f"name_{lang}") or reg_info.get("name_uz")
        text = get_text(
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
        try:
            await callback.message.edit_text(text, reply_markup=inline_kb, parse_mode=ParseMode.HTML)
        except Exception:
            pass
    await callback.answer()


def build_weekly_message(region_code: str, week_offset: int, weekly_data: list, lang: str = "uz") -> str:
    """Haftalik jadval matnini shakllantirish."""
    reg_info = config.REGIONS.get(region_code, config.REGIONS["tashkent"])
    hudud = reg_info.get(f"name_{lang}") or reg_info.get("name_uz")
    
    if not weekly_data:
        return get_text("error_loading", lang)
        
    start_date = weekly_data[0]["date"].strftime("%d.%m.%Y")
    end_date = weekly_data[-1]["date"].strftime("%d.%m.%Y")
    
    rows = []
    for item in weekly_data:
        d = item["date"].strftime("%d.%m")
        t = item["timings"]
        row = f"{d} | {t.get('fajr','--')} | {t.get('sunrise','--')} | {t.get('dhuhr','--')} | {t.get('asr','--')} | {t.get('maghrib','--')} | {t.get('isha','--')}"
        rows.append(row)
        
    rows_text = "\n".join(rows)
    return get_text("weekly_template", lang, start_date=start_date, end_date=end_date, hudud=hudud, rows=rows_text)


@router.message(F.text.in_([
    "📅 Haftalik jadval",
    "📅 Недельное расписание",
    "📅 Weekly schedule",
    "📅 Oylik jadval",
    "📅 Расписание на месяц"
]))
async def handle_weekly_schedule_btn(message: Message):
    """Haftalik jadval tugmasi."""
    user = await database.get_user(message.from_user.id)
    lang = user.get("language", "uz") if user else "uz"
    region_code = user.get("region", "tashkent") if user else "tashkent"
    
    today = prayer_api.get_current_datetime().date()
    weekly_data = await prayer_api.get_weekly_timings(region_code, today, days=7)
    
    text = build_weekly_message(region_code, 0, weekly_data, lang)
    kb = keyboards.get_weekly_nav_keyboard(lang, week_offset=0)
    await message.answer(text, reply_markup=kb, parse_mode=ParseMode.HTML)


@router.callback_query(F.data.startswith("week_nav:"))
async def cb_weekly_navigation(callback: CallbackQuery):
    """Haftalik jadvalda oldinga/orqaga o'tish."""
    week_offset = int(callback.data.split(":")[1])
    user = await database.get_user(callback.from_user.id)
    lang = user.get("language", "uz") if user else "uz"
    region_code = user.get("region", "tashkent") if user else "tashkent"
    
    base_date = prayer_api.get_current_datetime().date() + datetime.timedelta(days=week_offset * 7)
    weekly_data = await prayer_api.get_weekly_timings(region_code, base_date, days=7)
    
    text = build_weekly_message(region_code, week_offset, weekly_data, lang)
    kb = keyboards.get_weekly_nav_keyboard(lang, week_offset=week_offset)
    
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.HTML)
    except Exception:
        pass
    await callback.answer()
