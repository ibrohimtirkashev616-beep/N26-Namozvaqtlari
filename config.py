# -*- coding: utf-8 -*-
"""
Namoz Vaqtlari va Azon Eslatma Boti - Konfiguratsiya
O'zbekistonning barcha viloyat markazlari aniq koordinatalari bilan.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

raw_token = os.getenv("BOT_TOKEN", "").strip()
BOT_TOKEN = raw_token.replace(" ", "").replace("\n", "").replace("\r", "")

CALCULATION_METHOD = int(os.getenv("CALCULATION_METHOD", "3"))
TIMEZONE = os.getenv("TIMEZONE", "Asia/Tashkent")

DB_PATH = BASE_DIR / "namoz_bot.db"

# O'zbekistonning barcha viloyatlari va markazlarining aniq koordinatalari
REGIONS = {
    "tashkent": {
        "code": "tashkent",
        "name_uz": "Toshkent shahri",
        "name_ru": "г. Ташкент",
        "name_en": "Tashkent City",
        "button_uz": "🏙 Toshkent",
        "button_ru": "🏙 Ташкент",
        "button_en": "🏙 Tashkent",
        "latitude": 41.2995,
        "longitude": 69.2401,
    },
    "samarkand": {
        "code": "samarkand",
        "name_uz": "Samarqand",
        "name_ru": "Самарканд",
        "name_en": "Samarkand",
        "button_uz": "🕌 Samarqand",
        "button_ru": "🕌 Самарканд",
        "button_en": "🕌 Samarkand",
        "latitude": 39.6270,
        "longitude": 66.9750,
    },
    "fergana": {
        "code": "fergana",
        "name_uz": "Farg'ona (Qo'qon)",
        "name_ru": "Фергана (Коканд)",
        "name_en": "Fergana (Kokand)",
        "button_uz": "🌸 Farg'ona (Qo'qon)",
        "button_ru": "🌸 Фергана (Коканд)",
        "button_en": "🌸 Fergana (Kokand)",
        "latitude": 40.3842,
        "longitude": 71.7843,
    },
    "andijan": {
        "code": "andijan",
        "name_uz": "Andijon",
        "name_ru": "Андижан",
        "name_en": "Andijan",
        "button_uz": "🏞 Andijon",
        "button_ru": "🏞 Андижан",
        "button_en": "🏞 Andijan",
        "latitude": 40.7821,
        "longitude": 72.3442,
    },
    "namangan": {
        "code": "namangan",
        "name_uz": "Namangan",
        "name_ru": "Наманган",
        "name_en": "Namangan",
        "button_uz": "🌺 Namangan",
        "button_ru": "🌺 Наманган",
        "button_en": "🌺 Namangan",
        "latitude": 40.9983,
        "longitude": 71.6726,
    },
    "bukhara": {
        "code": "bukhara",
        "name_uz": "Buxoro",
        "name_ru": "Бухара",
        "name_en": "Bukhara",
        "button_uz": "🏛 Buxoro",
        "button_ru": "🏛 Бухара",
        "button_en": "🏛 Bukhara",
        "latitude": 39.7747,
        "longitude": 64.4286,
    },
    "khorezm": {
        "code": "khorezm",
        "name_uz": "Xorazm (Urganch)",
        "name_ru": "Хорезм (Ургенч)",
        "name_en": "Khorezm (Urgench)",
        "button_uz": "🏺 Urganch (Xorazm)",
        "button_ru": "🏺 Ургенч (Хорезм)",
        "button_en": "🏺 Urgench (Khorezm)",
        "latitude": 41.5506,
        "longitude": 60.6317,
    },
    "navoiy": {
        "code": "navoiy",
        "name_uz": "Navoiy",
        "name_ru": "Навои",
        "name_en": "Navoiy",
        "button_uz": "⚡️ Navoiy",
        "button_ru": "⚡️ Навои",
        "button_en": "⚡️ Navoiy",
        "latitude": 40.0844,
        "longitude": 65.3792,
    },
    "kashkadarya": {
        "code": "kashkadarya",
        "name_uz": "Qashqadaryo (Qarshi)",
        "name_ru": "Кашкадарья (Карши)",
        "name_en": "Kashkadarya (Karshi)",
        "button_uz": "🏰 Qarshi (Qashqadaryo)",
        "button_ru": "🏰 Карши (Кашкадарья)",
        "button_en": "🏰 Karshi (Kashkadarya)",
        "latitude": 38.8606,
        "longitude": 65.7891,
    },
    "surxondaryo": {
        "code": "surxondaryo",
        "name_uz": "Surxondaryo (Termiz)",
        "name_ru": "Сурхандарья (Термез)",
        "name_en": "Surkhandarya (Termez)",
        "button_uz": "☀️ Termiz (Surxondaryo)",
        "button_ru": "☀️ Термез (Сурхандарья)",
        "button_en": "☀️ Termez (Surkhandarya)",
        "latitude": 37.2242,
        "longitude": 67.2783,
    },
    "jizzakh": {
        "code": "jizzakh",
        "name_uz": "Jizzax",
        "name_ru": "Джизак",
        "name_en": "Jizzakh",
        "button_uz": "🌾 Jizzax",
        "button_ru": "🌾 Джизак",
        "button_en": "🌾 Jizzakh",
        "latitude": 40.1158,
        "longitude": 67.8422,
    },
    "sirdaryo": {
        "code": "sirdaryo",
        "name_uz": "Sirdaryo (Guliston)",
        "name_ru": "Сырдарья (Гулистан)",
        "name_en": "Sirdaryo (Gulistan)",
        "button_uz": "🌱 Guliston (Sirdaryo)",
        "button_ru": "🌱 Гулистан (Сырдарья)",
        "button_en": "🌱 Gulistan (Sirdaryo)",
        "latitude": 40.4897,
        "longitude": 68.7842,
    },
    "karakalpakstan": {
        "code": "karakalpakstan",
        "name_uz": "Qoraqalpog'iston (Nukus)",
        "name_ru": "Каракалпакстан (Нукус)",
        "name_en": "Karakalpakstan (Nukus)",
        "button_uz": "🏜 Nukus (Qoraqalpog'iston)",
        "button_ru": "🏜 Нукус (Каракалпакстан)",
        "button_en": "🏜 Nukus (Karakalpakstan)",
        "latitude": 42.4531,
        "longitude": 59.6103,
    }
}

# 5 vaqt namoz kalitlari
PRAYER_KEYS = ["fajr", "dhuhr", "asr", "maghrib", "isha"]
PRAYER_DISPLAY_KEYS = ["fajr", "sunrise", "dhuhr", "asr", "maghrib", "isha"]

DEFAULT_REMINDERS = {
    "fajr": True,
    "dhuhr": True,
    "asr": True,
    "maghrib": True,
    "isha": True,
}

REMINDER_BEFORE_OPTIONS = [0, 10, 15, 30]
DEFAULT_REMINDER_BEFORE = 0
