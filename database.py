# -*- coding: utf-8 -*-
"""
Ma'lumotlar bazasi (SQLite + aiosqlite)
Foydalanuvchi ma'lumotlari va namoz vaqtlari kesh jadvali
"""

import json
import logging
from typing import Optional, Dict, Any, List
import aiosqlite
import config

logger = logging.getLogger(__name__)


async def init_db():
    """Jadvallarni yaratish (users va prayer_times)."""
    async with aiosqlite.connect(config.DB_PATH) as db:
        # Foydalanuvchilar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                region TEXT NOT NULL DEFAULT 'tashkent',
                language TEXT NOT NULL DEFAULT 'uz',
                reminders TEXT NOT NULL,
                reminder_before INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Aladhan API dan yuklangan namoz vaqtlari jadvali
        await db.execute("""
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
        await db.commit()
    logger.info("Ma'lumotlar bazasi muvaffaqiyatli ishga tushirildi.")


async def save_prayer_times_to_db(
    region: str,
    date_str: str,
    fajr: str,
    sunrise: str,
    dhuhr: str,
    asr: str,
    maghrib: str,
    isha: str
) -> None:
    """Namoz vaqtlarini bazaga saqlash."""
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute("""
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
        """, (region, date_str, fajr, sunrise, dhuhr, asr, maghrib, isha))
        await db.commit()


async def get_prayer_times_from_db(region: str, date_str: str) -> Optional[Dict[str, str]]:
    """Bazadan saqlangan namoz vaqtlarini olish."""
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM prayer_times WHERE region = ? AND date = ?",
            (region, date_str)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return {
                    "fajr": row["fajr"],
                    "sunrise": row["sunrise"],
                    "dhuhr": row["dhuhr"],
                    "asr": row["asr"],
                    "maghrib": row["maghrib"],
                    "isha": row["isha"]
                }
    return None


async def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    """Foydalanuvchi ma'lumotlarini olish."""
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                data = dict(row)
                try:
                    data["reminders"] = json.loads(data["reminders"])
                except Exception:
                    data["reminders"] = config.DEFAULT_REMINDERS.copy()
                return data
    return None


async def create_or_update_user(
    user_id: int,
    region: Optional[str] = None,
    language: Optional[str] = None,
    reminders: Optional[Dict[str, bool]] = None,
    reminder_before: Optional[int] = None
) -> Dict[str, Any]:
    """Foydalanuvchini yaratish yoki yangilash."""
    existing = await get_user(user_id)
    
    current_region = region or (existing["region"] if existing else "tashkent")
    current_lang = language or (existing["language"] if existing else "uz")
    current_reminders = reminders or (existing["reminders"] if existing else config.DEFAULT_REMINDERS.copy())
    current_before = reminder_before if reminder_before is not None else (existing["reminder_before"] if existing else 0)
    
    reminders_json = json.dumps(current_reminders)
    
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute("""
            INSERT INTO users (user_id, region, language, reminders, reminder_before, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                region = excluded.region,
                language = excluded.language,
                reminders = excluded.reminders,
                reminder_before = excluded.reminder_before,
                updated_at = CURRENT_TIMESTAMP
        """, (user_id, current_region, current_lang, reminders_json, current_before))
        await db.commit()
        
    return {
        "user_id": user_id,
        "region": current_region,
        "language": current_lang,
        "reminders": current_reminders,
        "reminder_before": current_before
    }


async def set_user_region(user_id: int, region: str) -> None:
    """Foydalanuvchi hududini yangilash."""
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute(
            "UPDATE users SET region = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
            (region, user_id)
        )
        await db.commit()


async def set_user_language(user_id: int, language: str) -> None:
    """Foydalanuvchi tilini yangilash."""
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute(
            "UPDATE users SET language = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
            (language, user_id)
        )
        await db.commit()


async def toggle_prayer_reminder(user_id: int, prayer_name: str) -> Dict[str, bool]:
    """Bitta namoz eslatmasini yoqish/o'chirish."""
    user = await get_user(user_id)
    if not user:
        user = await create_or_update_user(user_id)
    
    reminders = user.get("reminders", config.DEFAULT_REMINDERS.copy())
    current_val = reminders.get(prayer_name, True)
    reminders[prayer_name] = not current_val
    
    reminders_json = json.dumps(reminders)
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute(
            "UPDATE users SET reminders = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
            (reminders_json, user_id)
        )
        await db.commit()
        
    return reminders


async def set_reminder_before(user_id: int, minutes: int) -> None:
    """Eslatma daqiqasini belgilash (0, 10, 15, 30)."""
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute(
            "UPDATE users SET reminder_before = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
            (minutes, user_id)
        )
        await db.commit()


async def get_all_users() -> List[Dict[str, Any]]:
    """Barcha foydalanuvchilarni olish (Scheduler uchun)."""
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users") as cursor:
            rows = await cursor.fetchall()
            result = []
            for row in rows:
                item = dict(row)
                try:
                    item["reminders"] = json.loads(item["reminders"])
                except Exception:
                    item["reminders"] = config.DEFAULT_REMINDERS.copy()
                result.append(item)
            return result
