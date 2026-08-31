# -*- coding: utf-8 -*-
import sys
import os
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

import asyncio
import datetime
import config
import database
import prayer_api
import keyboards
from texts import get_text, TEXTS, get_random_blessing


async def run_tests():
    print("=" * 60)
    print("  [TEST] NAMOZ VAQTLARI BOTI YANGILANGAN TESTLARI...")
    print("=" * 60)

    # 1. Baza testi
    print("\n1. Ma'lumotlar bazasi testlari:")
    await database.init_db()
    
    test_uid = 88888888
    user = await database.create_or_update_user(
        test_uid,
        region="fergana",
        language="en",
        reminders=config.DEFAULT_REMINDERS.copy(),
        reminder_before=10
    )
    assert user["region"] == "fergana", "Region mos kelmadi"
    assert user["language"] == "en", "English language mos kelmadi"
    print("  [OK] English tilida user yaratildi: region='fergana', lang='en'")

    # 2. 12+ viloyatlar va koordinatalar testi
    print("\n2. Viloyatlar va Aladhan API testlari:")
    assert len(config.REGIONS) >= 12, "Viloyatlar soni kamida 12 ta bo'lishi kerak"
    assert "fergana" in config.REGIONS, "Farg'ona topilmadi"
    assert config.REGIONS["fergana"]["name_uz"] == "Farg'ona (Qo'qon)", "Farg'ona (Qo'qon) nomi noto'g'ri"
    print(f"  [OK] Jami {len(config.REGIONS)} ta viloyat/hudud mavjud")

    today = prayer_api.get_current_datetime().date()
    
    # Farg'ona (Qo'qon) API testi
    fergana_timings = await prayer_api.get_timings("fergana", today)
    assert fergana_timings is not None, "Farg'ona vaqtlari olinmadi"
    print(f"  [OK] Farg'ona (Qo'qon) vaqtlari: {fergana_timings}")

    # Buxoro API testi
    bukhara_timings = await prayer_api.get_timings("bukhara", today)
    assert bukhara_timings is not None, "Buxoro vaqtlari olinmadi"
    print(f"  [OK] Buxoro vaqtlari: {bukhara_timings}")

    # 3. 3 ta tilda (UZ, RU, EN) hisoblash va matnlar testi
    print("\n3. 3 ta tilda (UZ, RU, EN) hisoblash va iliq ohang testlari:")
    # UZ
    p_name_uz, p_time_uz, t_left_uz = prayer_api.calculate_next_prayer(fergana_timings, "uz")
    print(f"  [OK] UZ: Keyingi namoz: {p_name_uz} ({p_time_uz}) - {t_left_uz}dan so'ng")
    
    # RU
    p_name_ru, p_time_ru, t_left_ru = prayer_api.calculate_next_prayer(fergana_timings, "ru")
    print(f"  [OK] RU: Следующий намаз: {p_name_ru} ({p_time_ru}) - через {t_left_ru}")

    # EN
    p_name_en, p_time_en, t_left_en = prayer_api.calculate_next_prayer(fergana_timings, "en")
    assert "hr" in t_left_en or "min" in t_left_en, "Inglizcha vaqt hisobi noto'g'ri"
    print(f"  [OK] EN: Next prayer: {p_name_en} ({p_time_en}) - in {t_left_en}")

    # 4. Tasodifiy iliq duolar testi
    print("\n4. Tasodifiy iliq duolar testi:")
    blessing_uz = get_random_blessing("uz")
    blessing_ru = get_random_blessing("ru")
    blessing_en = get_random_blessing("en")
    assert blessing_uz and blessing_ru and blessing_en, "Duo matnlari bo'sh"
    print(f"  [OK] UZ duo namunasi: '{blessing_uz}'")
    print(f"  [OK] RU duo namunasi: '{blessing_ru}'")
    print(f"  [OK] EN duo namunasi: '{blessing_en}'")

    # 5. Klaviaturalar (3 til va 12 viloyat) testi
    print("\n5. Klaviaturalar testi:")
    kb_lang = keyboards.get_language_inline_keyboard()
    # 3 ta til tugmasi borligini tekshirish
    all_lang_callbacks = [btn.callback_data for row in kb_lang.inline_keyboard for btn in row]
    assert "set_lang:uz" in all_lang_callbacks
    assert "set_lang:ru" in all_lang_callbacks
    assert "set_lang:en" in all_lang_callbacks
    print("  [OK] Til tanlash klaviaturasida 3 ta til mavjud (UZ, RU, EN)")

    kb_reg = keyboards.get_region_inline_keyboard("uz")
    assert len(kb_reg.inline_keyboard) >= 6, "Viloyatlar 2 ustunli bo'lib joylashgan"
    print("  [OK] Viloyat tanlash klaviaturasi to'g'ri generatsiya qilindi")

    kb_main_en = keyboards.get_main_reply_keyboard("en")
    assert kb_main_en.keyboard[0][0].text == "🕌 Today's prayer times"
    print("  [OK] English asosiy menyusi to'g'ri")

    print("\n" + "=" * 60)
    print("  BARCHA YANGI IMKONIYATLAR VA TESTLAR MUVAFFAQITYATLI O'TDI! [OK]")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_tests())
