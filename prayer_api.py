# -*- coding: utf-8 -*-
"""
Aladhan API orqali namoz vaqtlarini olish va hisoblash
Barcha 12 viloyat markazi va 3 til (uz, ru, en) uchun optimallashtirilgan kesh bilan.
"""

import aiohttp
import asyncio
import logging
import datetime
from typing import Dict, Any, Optional, List, Tuple
import pytz
import config
from texts import PRAYER_NAMES, MONTHS, WEEKDAYS

logger = logging.getLogger(__name__)
tz = pytz.timezone(config.TIMEZONE)

# Keshlash: {(region, date_str): timings_dict}
_TIMINGS_CACHE: Dict[Tuple[str, str], Dict[str, str]] = {}


def get_current_datetime() -> datetime.datetime:
    """O'zbekiston vaqti bo'yicha joriy sana va vaqt."""
    return datetime.datetime.now(tz)


async def fetch_timings_from_api(region_code: str, target_date: datetime.date) -> Optional[Dict[str, str]]:
    """Aladhan API dan berilgan sana uchun vaqtlarni yuklab olish."""
    reg_info = config.REGIONS.get(region_code)
    if not reg_info:
        return None
        
    date_str = target_date.strftime("%d-%m-%Y")
    cache_key = (region_code, date_str)
    
    if cache_key in _TIMINGS_CACHE:
        return _TIMINGS_CACHE[cache_key]
        
    url = f"https://api.aladhan.com/v1/timings/{date_str}"
    params = {
        "latitude": reg_info["latitude"],
        "longitude": reg_info["longitude"],
        "method": config.CALCULATION_METHOD,
        "school": 1
    }
    
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    raw_timings = data.get("data", {}).get("timings", {})
                    
                    cleaned = {
                        "fajr": raw_timings.get("Fajr", "00:00").split(" ")[0][:5],
                        "sunrise": raw_timings.get("Sunrise", "00:00").split(" ")[0][:5],
                        "dhuhr": raw_timings.get("Dhuhr", "00:00").split(" ")[0][:5],
                        "asr": raw_timings.get("Asr", "00:00").split(" ")[0][:5],
                        "maghrib": raw_timings.get("Maghrib", "00:00").split(" ")[0][:5],
                        "isha": raw_timings.get("Isha", "00:00").split(" ")[0][:5],
                    }
                    _TIMINGS_CACHE[cache_key] = cleaned
                    return cleaned
                else:
                    logger.error(f"Aladhan API xatosi {resp.status} for {region_code} on {date_str}")
    except Exception as e:
        logger.error(f"Aladhan API so'rovida xatolik: {e}")
        
    return None


async def get_timings(region_code: str, target_date: Optional[datetime.date] = None) -> Optional[Dict[str, str]]:
    """Vaqtlarni olish (kesh yoki API)."""
    if target_date is None:
        target_date = get_current_datetime().date()
    return await fetch_timings_from_api(region_code, target_date)


async def get_weekly_timings(region_code: str, start_date: datetime.date, days: int = 7) -> List[Dict[str, Any]]:
    """Haftalik jadvalni olish."""
    results = []
    tasks = []
    dates = [start_date + datetime.timedelta(days=i) for i in range(days)]
    
    for d in dates:
        tasks.append(get_timings(region_code, d))
        
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    for d, resp in zip(dates, responses):
        if isinstance(resp, dict):
            results.append({
                "date": d,
                "timings": resp
            })
    return results


def calculate_next_prayer(timings: Dict[str, str], lang: str = "uz") -> Tuple[str, str, str]:
    """
    Keyingi namoz nomi, vaqti va qolgan vaqtni hisoblash.
    Qaytaradi: (namoz_nomi, namoz_vaqti, qolgan_vaqt_matni)
    """
    now = get_current_datetime()
    current_minutes = now.hour * 60 + now.minute
    
    prayer_order = [
        ("fajr", timings.get("fajr", "04:30")),
        ("sunrise", timings.get("sunrise", "06:00")),
        ("dhuhr", timings.get("dhuhr", "12:30")),
        ("asr", timings.get("asr", "16:00")),
        ("maghrib", timings.get("maghrib", "19:00")),
        ("isha", timings.get("isha", "20:30")),
    ]
    
    next_key = None
    next_time_str = None
    diff_minutes = 0
    
    for key, time_str in prayer_order:
        try:
            h, m = map(int, time_str.split(":"))
            p_minutes = h * 60 + m
            if p_minutes > current_minutes:
                next_key = key
                next_time_str = time_str
                diff_minutes = p_minutes - current_minutes
                break
        except Exception:
            continue
            
    # Agar barcha namozlar o'tgan bo'lsa -> ertangi Bomdod
    if next_key is None:
        next_key = "fajr"
        next_time_str = timings.get("fajr", "04:30")
        try:
            h, m = map(int, next_time_str.split(":"))
            fajr_minutes = h * 60 + m
            diff_minutes = (24 * 60 - current_minutes) + fajr_minutes
        except Exception:
            diff_minutes = 300
            
    hours, mins = divmod(diff_minutes, 60)
    
    if lang == "ru":
        if hours > 0 and mins > 0:
            time_left = f"{hours} ч. {mins} мин."
        elif hours > 0:
            time_left = f"{hours} ч."
        else:
            time_left = f"{mins} мин."
    elif lang == "en":
        if hours > 0 and mins > 0:
            time_left = f"{hours} hr {mins} min"
        elif hours > 0:
            time_left = f"{hours} hr"
        else:
            time_left = f"{mins} min"
    else:
        if hours > 0 and mins > 0:
            time_left = f"{hours} soat {mins} daqiqa"
        elif hours > 0:
            time_left = f"{hours} soat"
        else:
            time_left = f"{mins} daqiqa"
            
    p_name = PRAYER_NAMES.get(lang, {}).get(next_key, next_key)
    return p_name, next_time_str, time_left


def format_date_title(target_date: datetime.date, lang: str = "uz") -> Tuple[str, str]:
    """Sana va hafta kunini formatlash."""
    day = target_date.day
    month_name = MONTHS.get(lang, {}).get(target_date.month, "")
    year = target_date.year
    weekday_name = WEEKDAYS.get(lang, WEEKDAYS["uz"])[target_date.weekday()]
    
    if lang == "ru":
        sana = f"{day} {month_name} {year}"
    elif lang == "en":
        sana = f"{month_name} {day}, {year}"
    else:
        sana = f"{day}-{month_name}, {year}"
        
    return sana, weekday_name
