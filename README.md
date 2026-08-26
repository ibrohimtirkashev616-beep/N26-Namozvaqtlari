# 🤖 AI HR Agent Telegram Boti

Sun'iy Intellekt (**OpenAI GPT-4o-mini**) asosida ishlovchi aqlli **HR Agent Telegram Boti**. Ushbu bot nomzodlarning arizalari va rezyumelarini (PDF/DOCX) chuqur tahlil qilib, vakansiyaga mosligini baholaydi va saralangan holda HR guruhiga yuboradi.

---

## 🌟 Asosiy Imkoniyatlar

1. **📝 Nomzodlar uchun qulay ariza topshirish tizimi:**
   - Bo'sh ish o'rinlari (vakansiyalar) ro'yxatidan tanlash.
   - Bosqichma-bosqich anketa (F.I.SH, Telefon raqam, Ish tajribasi, Kutilayotgan maosh, Portfolio/GitHub).
   - Rezyumeni (CV) **PDF** yoki **DOCX** formatda yuklash (yoki to'g'ridan-to'g'ri matn ko'rinishida yuborish).

2. **🤖 Sun'iy Intellekt (OpenAI) Tahlili:**
   - **Moslik darajasi (Match Score):** 0% dan 100% gacha aniq baholash.
   - **Kategoriyalash:**
     - 🟢 **MOS KELDI** (>= 75%) — Vakansiya talablariga to'liq javob beruvchi nomzodlar.
     - 🟡 **QISMAN MOS** (50% - 74%) — Qisman mos, o'rganish salohiyati bor nomzodlar.
     - 🔴 **MOS KELMADI** (< 50%) — Talabga javob bermaydigan nomzodlar.
   - **Kuchli tomonlar va Kamchiliklar:** Texnologik stek va tajriba bo'yicha tahlil.
   - **HR uchun tavsiya:** Suhbatga chaqirish yoki rad etish bo'yicha amaliy maslahat.
   - **Suhbat savollari:** Nomzodning rezyumesi asosida maxsus generatsiya qilingan 3 ta texnik va professional savol.

3. **👥 Telegram Guruh Integratsiyasi (HR Jamoasi uchun):**
   - Har bir yangi ariza guruhga chiroyli va to'liq formatlangan kartochka ko'rinishida yuboriladi.
   - Nomzod yuklagan rezyume hujjati (PDF/DOCX) ham to'g'ridan-to'g'ri guruhga biriktiriladi.
   - **Interaktiv tugmalar (Guruh boshqaruvi):**
     - `✅ Suhbatga chaqirish` — Nomzodga shaxsiy xabar orqali xushxabar yuboradi.
     - `❌ Rad etish` — Nomzodga xushmuomalalik bilan rad javobini yetkazadi.
     - `⭐ Zaxiraga olish` — Nomzodni Talent Pool (zaxira) ga kiritadi.
     - `💬 Xabar yuborish` — HR mutaxassisi nomzodga maxsus xabar yozishi mumkin.

4. **⚡ Tezkor CV Tahlili (Self-check):**
   - Nomzod ariza topshirmasdan turib ham o'z rezyumesini istalgan yo'nalish bo'yicha AI orqali tekshirib olishi mumkin.

5. **📊 HR Statistikasi:**
   - `/stats` buyrug'i orqali qabul qilingan arizalar, saralash foizi va HR qarorlari hisoboti.

---

## 📁 Loyiha Strukturasi

```
N26 NAJOTTALIM/
├── config.py                  # Konfiguratsiya, vakansiyalar va talablar
├── hr_bot.py                  # Asosiy botni ishga tushiruvchi fayl
├── states.py                  # Aiogram FSM holatlari
├── test_hr_system.py          # Baza va AI tahlili integratsiya testi
├── .env                       # Bot tokeni, OpenAI kaliti va Guruh ID
├── .env.example               # Namuna sozlamalar
├── requirements.txt           # Kerakli Python kutubxonalari
│
├── handlers/                  # Bot buyruqlari va xabarlar handleri
│   ├── __init__.py
│   ├── common.py              # /start, /help, bo'sh ish o'rinlari, arizalarim
│   ├── candidate.py           # Ariza topshirish va CV tahlili
│   └── admin.py               # Guruhdagi tugmalar, HR qarorlari, /stats
│
├── services/                  # Asosiy biznes logika va servislar
│   ├── __init__.py
│   ├── ai_agent.py            # OpenAI GPT-4o-mini tahlil tizimi
│   └── database.py            # SQLite (aiosqlite) ma'lumotlar bazasi
│
└── utils/                     # Yordamchi modullar
    ├── __init__.py
    ├── document_parser.py     # PDF va DOCX fayllardan matn ajratish
    └── formatters.py          # Telegram HTML xabar shablonlari
```

---

## ⚙️ O'rnatish va Ishga Tushirish

### 1. Talablar:
- Python 3.10+
- Telegram Bot Token
- OpenAI API Key

### 2. Kutubxonalarni o'rnatish:
```bash
pip install -r requirements.txt
```

### 3. `.env` faylini sozlash:
`.env` faylida quyidagi ma'lumotlar kiritilgan:
```env
BOT_TOKEN=your_telegram_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
HR_GROUP_ID=-5311202670
```

> **Muhim eslatma:** Bot arizalarni Telegram guruhga yuborishi uchun:
> 1. `@n26najottalim_bot` ni o'sha Telegram guruhga (**ID:** `-5311202670`) a'zo qilib qo'shing.
> 2. Botga guruhda **Admin** huquqini (xabar yozish ruxsatini) bering.

### 4. Botni ishga tushirish:
```bash
python hr_bot.py
```

### 5. Tizimni sinovdan o'tkazish:
```bash
python test_hr_system.py
```
