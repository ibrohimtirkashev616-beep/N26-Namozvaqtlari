"""
HR Agent Bot - Sozlamalar va Konfiguratsiya
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Asosiy yo'l
BASE_DIR = Path(__file__).resolve().parent

# .env yuklash
load_dotenv(BASE_DIR / ".env")

# Bot va OpenAI sozlamalari
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()

# HR Guruhi ID si
raw_group_id = os.getenv("HR_GROUP_ID", "-5311202670").strip()
try:
    HR_GROUP_ID = int(raw_group_id)
except ValueError:
    HR_GROUP_ID = -5311202670

# Adminlar ro'yxati (ixtiyoriy)
ADMIN_IDS = []
raw_admin_ids = os.getenv("ADMIN_IDS", "").strip()
if raw_admin_ids:
    for aid in raw_admin_ids.split(","):
        aid_clean = aid.strip()
        if aid_clean.isdigit() or (aid_clean.startswith("-") and aid_clean[1:].isdigit()):
            ADMIN_IDS.append(int(aid_clean))

# Ma'lumotlar bazasi yo'li
DB_PATH = BASE_DIR / "hr_database.db"

# Vaqtinchalik fayllar uchun papka
DOWNLOADS_DIR = BASE_DIR / "temp_resumes"
DOWNLOADS_DIR.mkdir(exist_ok=True)

# Vakansiyalar va ularning talablari (AI tahlili uchun mezonlar)
VACANCIES = {
    "python_backend": {
        "title": "🐍 Python Backend Dasturchi",
        "description": "Python, Django/FastAPI, PostgreSQL va mikroxizmatlar bilan ishlash.",
        "requirements": """
- Python 3.10+ bilimi, OOP va toza kod prinsiplari (SOLID, DRY)
- FastAPI yoki Django / Django REST Framework
- PostgreSQL, SQLAlchemy / Django ORM, ma'lumotlar bazasi optimizatsiyasi
- Redis, Celery yoki RabbitMQ bilan ishlash tajribasi
- Docker va Docker Compose asoslari
- Git va CI/CD tushunchasi
- Kamida 1+ yil tijoriy tajriba
"""
    },
    "frontend_dev": {
        "title": "⚛️ Frontend Dasturchi (React / Vue)",
        "description": "Zamonaviy veb interfeyslar va SPA/SSR ilovalar yaratish.",
        "requirements": """
- JavaScript (ES6+) va TypeScript bilimi
- React.js / Next.js yoki Vue.js / Nuxt.js
- HTML5, CSS3, SCSS, Tailwind CSS
- REST API va GraphQL bilan integratsiya
- State Management (Redux Toolkit, Zustand yoki Pinia)
- Webpack / Vite va Git bilan ishlash
- Kamida 1+ yil tijoriy tajriba
"""
    },
    "mobile_dev": {
        "title": "📱 Mobil Dasturchi (Flutter / iOS / Android)",
        "description": "iOS va Android uchun kross-platforma yoki nativ ilovalar.",
        "requirements": """
- Flutter / Dart yoki Swift / Kotlin bo'yicha mustahkam bilim
- State management (BLoC, Provider yoki Riverpod)
- REST API / WebSocket integratsiyasi
- App Store va Google Play ga chiqarish tajribasi
- Clean Architecture va UI/UX qoidalariga rioya qilish
- Kamida 1+ yil tajriba
"""
    },
    "ui_ux_designer": {
        "title": "🎨 UI/UX Dizayner",
        "description": "Foydalanuvchi interfeysi va tajribasi dizayni.",
        "requirements": """
- Figma dasturida professional ishlash (Auto-layout, Components, Variants)
- Wireframing, Prototyping va User Flow yaratish
- Design Systems yaratish va qo'llab-quvvatlash
- Foydalanuvchilar tadqiqoti (User Research) va testlash
- Portfolio (veb va mobil loyihalar mavjudligi)
- Kamida 1+ yil tajriba
"""
    },
    "project_manager": {
        "title": "📋 Project Manager / Scrum Master",
        "description": "IT loyihalarni boshqarish va jamoa ishini tashkillashtirish.",
        "requirements": """
- Agile, Scrum, Kanban metodologiyalarini mukammal bilish
- Jira, Trello, Confluence va Notion vositalaridan foydalanish
- Texnik topshiriqlar (SRS, User Stories) yozish ko'nikmasi
- Jamoada muloqot va liderlik qobiliyati
- IT loyihalarda kamida 2+ yil tajriba
"""
    },
    "qa_engineer": {
        "title": "🧪 QA Muhandis (Manual / Automation)",
        "description": "Dasturiy ta'minot sifatini ta'minlash va testlash.",
        "requirements": """
- Test-keys, test-plan va bug reportlar yozish
- API testlash (Postman, Swagger)
- Avtomatlashtirilgan testlar asoslari (Selenium, Playwright yoki PyTest)
- SQL asosiy so'rovlari
- Kamida 1+ yil tajriba
"""
    },
    "smm_marketing": {
        "title": "📢 SMM & Kontent Menejer",
        "description": "Ijtimoiy tarmoqlarni yuritish va marketing kampaniyalari.",
        "requirements": """
- Instagram, Telegram, LinkedIn va TikTok uchun kontent reja tuzish
- Qiziqarli matnlar yozish (kopirayting)
- Reels va qisqa videolar uchun ssenariylar tayyorlash
- Target reklama asoslari va tahlil qilish (Analytics)
- Kamida 1+ yil tajriba
"""
    },
    "other": {
        "title": "💼 Boshqa yo'nalish",
        "description": "Boshqa mutaxassisliklar yoki umumiy ariza.",
        "requirements": """
- O'z sohasida professional bilim va amaliy tajriba
- Mas'uliyat, jamoada ishlash va o'rganishga bo'lgan yuqori qobiliyat
"""
    }
}
