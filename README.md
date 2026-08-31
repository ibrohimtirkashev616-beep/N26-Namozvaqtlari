# 🕌 Namoz Vaqtlari va Azon Eslatma Telegram Boti

Ushbu Telegram bot Toshkent va Samarqand hududlari uchun aniq kunlik namoz vaqtlarini (Aladhan API asosida) ko'rsatadi, haftalik jadvalni taqdim etadi hamda har bir namoz vaqti uchun sozlanuvchan azon va eslatma (push-xabar) yuborish imkoniyatiga ega.

---

## 🌟 Asosiy Imkoniyatlar

1. **📍 2 ta Hudud:** Toshkent va Samarqand (boshqa viloyatlarsiz).
2. **🗣 2 ta Til:** O'zbek tili (`uz`) va Rus tili (`ru`).
3. **🕌 5 Mahal Namoz Jadvali:** Bomdod, Peshin, Asr, Shom, Xufton va Quyosh chiqish vaqti.
4. **⏳ Keyingi Namoz Hisoblagichi:** Keyingi kiradigan namoz vaqti va unga qancha vaqt qolganligini real vaqtda aniqlash.
5. **📅 Haftalik Jadval:** Bir haftalik to'liq namoz vaqtlari jadvali va oldingi/keyingi haftaga o'tish (`◀️` / `▶️`).
6. **🔔 Moslashuvchan Eslatmalar (APScheduler):**
   - Har bir namoz uchun alohida yoqish/o'chirish (`✅` / `❌`).
   - Eslatma vaqti: **Vaqtida**, **10 daqiqa oldin**, **15 daqiqa oldin**, **30 daqiqa oldin**.
7. **⚙️ Sozlamalar:** Hudud, til va eslatmalarni istalgan paytda o'zgartirish.

---

## 📁 Loyiha Strukturasi

```
N26 NAJOTTALIM/
├── bot.py                  # Asosiy ishga tushirish fayli (aiogram 3 + APScheduler)
├── config.py               # Token, shahar koordinatalari va sozlamalar
├── database.py             # SQLite (aiosqlite) ma'lumotlar bazasi (CRUD)
├── prayer_api.py           # Aladhan API va hisoblash logikasi
├── scheduler.py            # APScheduler kunlik eslatmalar xizmati
├── texts.py                # O'zbek va Rus tillaridagi xabar shablonlari
├── keyboards.py            # Inline va Reply menyu klaviaturalari
├── test_bot_suite.py       # To'liq integratsion testlar
├── requirements.txt        # Kerakli Python kutubxonalari
├── .env                    # Bot tokeni va sozlamalar
└── handlers/
    ├── __init__.py
    ├── start.py            # /start, /help, til va hudud tanlash
    ├── prayer.py           # Bugungi/ertangi vaqtlar, yangilash, haftalik jadval
    ├── reminders.py        # Eslatmalarni sozlash va daqiqalarni tanlash
    ├── settings.py         # Sozlamalar (hudud, til, eslatmalar)
    └── unknown.py          # Noma'lum xabarlarga xushmuomala javob
```

---

## ⚙️ O'rnatish va Ishga Tushirish

### 1. Kutubxonalarni o'rnatish:
```bash
pip install -r requirements.txt
```

### 2. Testlarni ishga tushirish:
```bash
python test_bot_suite.py
```

### 3. Botni ishga tushirish:
```bash
python bot.py
```
