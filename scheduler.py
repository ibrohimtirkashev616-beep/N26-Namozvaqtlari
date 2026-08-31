# -*- coding: utf-8 -*-
"""
APScheduler orqali eslatmalarni belgilangan vaqtda yuborish
Har daqiqada tekshirib, barcha viloyatlar uchun push-xabar yuboradi.
Iliq, samimiy diniy duo va jumlalar bilan.
"""

import asyncio
import logging
import datetime
from typing import Set, Tuple
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
import config
import database
import prayer_api
from texts import get_text, PRAYER_NAMES, get_random_blessing

logger = logging.getLogger(__name__)

# Takroriy yuborilmasligi uchun kesh: (user_id, prayer_name, date_str, trigger_type)
_SENT_REMINDERS_CACHE: Set[Tuple[int, str, str, str]] = set()


async def check_and_send_prayer_reminders(bot: Bot):
    """Har daqiqada ishlovchi tekshirish va eslatma yuborish funksiyasi."""
    try:
        now = prayer_api.get_current_datetime()
        today = now.date()
        date_str = today.strftime("%Y-%m-%d")
        current_time_str = now.strftime("%H:%M")
        
        # 1. Barcha viloyatlar uchun bugungi vaqtlarni yuklash
        timings_map = {}
        for r_code in config.REGIONS.keys():
            t = await prayer_api.get_timings(r_code, today)
            if t:
                timings_map[r_code] = t
                
        if not timings_map:
            return
            
        # 2. Bazadagi barcha foydalanuvchilarni olish
        users = await database.get_all_users()
        if not users:
            return
            
        for user in users:
            user_id = user["user_id"]
            region_code = user.get("region", "tashkent")
            lang = user.get("language", "uz")
            reminders = user.get("reminders", config.DEFAULT_REMINDERS)
            reminder_before = user.get("reminder_before", 0)
            
            timings = timings_map.get(region_code)
            if not timings:
                continue
                
            reg_info = config.REGIONS.get(region_code, config.REGIONS["tashkent"])
            hudud_name = reg_info.get(f"name_{lang}") or reg_info.get("name_uz")
            
            for prayer_key in config.PRAYER_KEYS:
                if not reminders.get(prayer_key, True):
                    continue
                    
                p_time_str = timings.get(prayer_key)
                if not p_time_str or ":" not in p_time_str:
                    continue
                    
                try:
                    p_h, p_m = map(int, p_time_str.split(":"))
                    prayer_dt = now.replace(hour=p_h, minute=p_m, second=0, microsecond=0)
                except Exception:
                    continue
                    
                trigger_dt = prayer_dt - datetime.timedelta(minutes=reminder_before)
                trigger_time_str = trigger_dt.strftime("%H:%M")
                
                if current_time_str == trigger_time_str:
                    trigger_tag = f"before_{reminder_before}" if reminder_before > 0 else "ontime"
                    cache_key = (user_id, prayer_key, date_str, trigger_tag)
                    
                    if cache_key in _SENT_REMINDERS_CACHE:
                        continue
                        
                    _SENT_REMINDERS_CACHE.add(cache_key)
                    
                    p_name = PRAYER_NAMES.get(lang, {}).get(prayer_key, prayer_key)
                    blessing = get_random_blessing(lang)
                    
                    if reminder_before == 0:
                        msg_text = get_text(
                            "ontime_reminder",
                            lang,
                            namoz_nomi=p_name,
                            hudud=hudud_name,
                            vaqt=p_time_str,
                            blessing=blessing
                        )
                    else:
                        msg_text = get_text(
                            "advance_reminder",
                            lang,
                            namoz_nomi=p_name,
                            daqiqa=reminder_before,
                            vaqt=p_time_str,
                            hudud=hudud_name,
                            blessing=blessing
                        )
                        
                    try:
                        await bot.send_message(
                            chat_id=user_id,
                            text=msg_text,
                            parse_mode=ParseMode.HTML
                        )
                        logger.info(f"Eslatma yuborildi: user={user_id}, prayer={prayer_key}, region={region_code}, before={reminder_before}")
                    except TelegramForbiddenError:
                        logger.warning(f"Foydalanuvchi botni bloklagan: user={user_id}")
                    except Exception as e:
                        logger.error(f"Eslatma yuborishda xatolik: user={user_id}, err={e}")

        if len(_SENT_REMINDERS_CACHE) > 5000:
            _SENT_REMINDERS_CACHE.clear()
            
    except Exception as e:
        logger.error(f"Scheduler siklida umumiy xatolik: {e}")


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    """APScheduler ni sozlash."""
    scheduler = AsyncIOScheduler(timezone=config.TIMEZONE)
    scheduler.add_job(
        check_and_send_prayer_reminders,
        trigger="interval",
        minutes=1,
        args=[bot],
        id="prayer_reminders_job",
        replace_existing=True
    )
    return scheduler
