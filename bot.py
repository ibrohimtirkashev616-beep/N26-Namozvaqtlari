# -*- coding: utf-8 -*-
"""
Namoz Vaqtlari va Azon Eslatma Telegram Boti
Asosiy ishga tushirish fayli (aiogram 3 + APScheduler)
O'zbekistonning barcha 12 viloyat markazi va Qoraqalpog'iston uchun
Aladhan API (method=3, school=1) integratsiyasi.
"""

import sys
import os
import asyncio
import logging
import datetime
import sqlite3
import requests
from pathlib import Path
from typing import Dict, Any, Optional

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram.client.default import DefaultBotProperties
from aiogram.client.telegram import TelegramAPIServer
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode

import config
import database
from scheduler import setup_scheduler
from handlers.start import router as start_router
from handlers.prayer import router as prayer_router
from handlers.reminders import router as reminders_router
from handlers.settings import router as settings_router
from handlers.unknown import router as unknown_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("NamozBot")

# O'zbekistonning barcha 12 ta viloyat markazi va Nukusning aniq koordinatalari
REGION_COORDINATES = {
    "tashkent": {"lat": 41.2995, "lng": 69.2401, "name_uz": "Toshkent shahri"},
    "samarkand": {"lat": 39.6270, "lng": 66.9750, "name_uz": "Samarqand"},
    "fergana": {"lat": 40.3842, "lng": 71.7843, "name_uz": "Farg'ona (Qo'qon)"},
    "andijan": {"lat": 40.7821, "lng": 72.3442, "name_uz": "Andijon"},
    "namangan": {"lat": 40.9983, "lng": 71.6726, "name_uz": "Namangan"},
    "bukhara": {"lat": 39.7747, "lng": 64.4286, "name_uz": "Buxoro"},
    "khorezm": {"lat": 41.5506, "lng": 60.6317, "name_uz": "Xorazm (Urganch)"},
    "navoiy": {"lat": 40.0844, "lng": 65.3792, "name_uz": "Navoiy"},
    "kashkadarya": {"lat": 38.8606, "lng": 65.7891, "name_uz": "Qashqadaryo (Qarshi)"},
    "surxondaryo": {"lat": 37.2242, "lng": 67.2783, "name_uz": "Surxondaryo (Termiz)"},
    "jizzakh": {"lat": 40.1158, "lng": 67.8422, "name_uz": "Jizzax"},
    "sirdaryo": {"lat": 40.4897, "lng": 68.7842, "name_uz": "Sirdaryo (Guliston)"},
    "karakalpakstan": {"lat": 42.4531, "lng": 59.6103, "name_uz": "Qoraqalpog'iston (Nukus)"}
}


def get_and_save_aladhan_prayer_times(region: str, sana: Optional[str] = None) -> Dict[str, Any]:
    """
    Aladhan API orqali barcha viloyatlar uchun namoz vaqtlarini olish va bazaga saqlash.

    Parametrlar:
      - region: viloyat kodi (tashkent, samarkand, fergana, andijan, namangan, bukhara,
                khorezm, navoiy, kashkadarya, surxondaryo, jizzakh, sirdaryo, karakalpakstan)
      - sana: 'DD-MM-YYYY' formatidagi sana (agar berilmasa, bugungi sana)

    Qaytaradi:
      - Muvaffaqiyatli: 5 mahal namoz va quyosh vaqtlari (method=3, school=1)
      - Xatolik: {"error": "Kechirasiz, hozircha bu ma'lumotni topa olmadim, birozdan so'ng qayta urinib ko'ring 🙏"}
    """
    region_key = region.lower().strip()
    if region_key not in REGION_COORDINATES:
        logger.warning(f"Noma'lum hudud: {region}")
        return {"error": "Kechirasiz, hozircha bu ma'lumotni topa olmadim, birozdan so'ng qayta urinib ko'ring 🙏"}

    if not sana:
        sana = datetime.datetime.now().strftime("%d-%m-%Y")

    coords = REGION_COORDINATES[region_key]
    url = f"https://api.aladhan.com/v1/timings/{sana}"
    params = {
        "latitude": coords["lat"],
        "longitude": coords["lng"],
        "method": 3,
        "school": 1
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            timings = data.get("data", {}).get("timings", {})

            fajr = timings.get("Fajr", "").split(" ")[0][:5]
            sunrise = timings.get("Sunrise", "").split(" ")[0][:5]
            dhuhr = timings.get("Dhuhr", "").split(" ")[0][:5]
            asr = timings.get("Asr", "").split(" ")[0][:5]
            maghrib = timings.get("Maghrib", "").split(" ")[0][:5]
            isha = timings.get("Isha", "").split(" ")[0][:5]

            # SQLite ma'lumotlar bazasiga saqlash
            conn = sqlite3.connect(config.DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prayer_times (
                    region TEXT NOT NULL,
                    date TEXT NOT NULL,
                    fajr TEXT NOT NULL,
                    sunrise TEXT NOT NULL,
                    dhuhr TEXT NOT NULL,
                    asr TEXT NOT NULL,
                    maghrib TEXT NOT NULL,
                    isha TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (region, date)
                )
            """)
            cursor.execute("""
                INSERT INTO prayer_times (region, date, fajr, sunrise, dhuhr, asr, maghrib, isha, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(region, date) DO UPDATE SET
                    fajr = excluded.fajr,
                    sunrise = excluded.sunrise,
                    dhuhr = excluded.dhuhr,
                    asr = excluded.asr,
                    maghrib = excluded.maghrib,
                    isha = excluded.isha,
                    created_at = CURRENT_TIMESTAMP
            """, (region_key, sana, fajr, sunrise, dhuhr, asr, maghrib, isha))
            conn.commit()
            conn.close()

            logger.info(f"Aladhan API dan {region_key} ({sana}) uchun namoz vaqtlari saqlandi.")
            return {
                "status": "success",
                "region": region_key,
                "date": sana,
                "fajr": fajr,
                "sunrise": sunrise,
                "dhuhr": dhuhr,
                "asr": asr,
                "maghrib": maghrib,
                "isha": isha
            }
        else:
            logger.error(f"Aladhan API xatosi: status {response.status_code}")
            return {"error": "Kechirasiz, hozircha bu ma'lumotni topa olmadim, birozdan so'ng qayta urinib ko'ring 🙏"}
    except requests.exceptions.RequestException as e:
        logger.error(f"Aladhan API so'rovida tarmoq xatoligi: {e}")
        return {"error": "Kechirasiz, hozircha bu ma'lumotni topa olmadim, birozdan so'ng qayta urinib ko'ring 🙏"}
    except Exception as e:
        logger.error(f"Kutilmagan xatolik: {e}")
        return {"error": "Kechirasiz, hozircha bu ma'lumotni topa olmadim, birozdan so'ng qayta urinib ko'ring 🙏"}


async def setup_commands(bot: Bot):
    """Telegram menyusiga asosiy buyruqlarni o'rnatish."""
    commands = [
        BotCommand(command="start", description="🤖 Botni ishga tushirish / Restart"),
        BotCommand(command="help", description="ℹ️ Yordam va ma'lumot / Help"),
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())


async def main():
    logger.info("=" * 55)
    logger.info("  🕌 NAMOZ VAQTLARI VA AZON ESLATMA BOTI ISHGA TUSHMOQDA...")
    logger.info("=" * 55)

    if not config.BOT_TOKEN:
        logger.critical("XATOLIK: .env faylida BOT_TOKEN ko'rsatilmagan!")
        return

    # 1. Baza initsializatsiyasi
    await database.init_db()

    # 2. Bot va Dispatcher
    session = AiohttpSession(timeout=300)
    if config.USE_LOCAL_BOT_API:
        custom_server = TelegramAPIServer.from_base(config.LOCAL_BOT_API_URL, is_local=True)
        bot = Bot(
            token=config.BOT_TOKEN,
            session=session,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
            server=custom_server
        )
        logger.info(f"Local Telegram Bot API serveriga ulanmoqda: {config.LOCAL_BOT_API_URL}")
    else:
        bot = Bot(
            token=config.BOT_TOKEN,
            session=session,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
    dp = Dispatcher()

    # 3. Routerlarni ulash (tartib muhim!)
    dp.include_router(start_router)
    dp.include_router(prayer_router)
    dp.include_router(reminders_router)
    dp.include_router(settings_router)
    dp.include_router(unknown_router)

    # 4. APScheduler ni ishga tushirish
    scheduler = setup_scheduler(bot)
    scheduler.start()
    logger.info("APScheduler eslatma xizmati ishga tushdi.")

    # 5. Bot ma'lumotlari va menyu
    try:
        bot_info = await bot.get_me()
        logger.info(f"Bot ulandi: @{bot_info.username} (ID: {bot_info.id})")
        await setup_commands(bot)
    except Exception as e:
        logger.error(f"Bot ulanishida xatolik: {e}")

    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bot tayyor! (Polling boshlandi)")

    try:
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
