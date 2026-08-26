"""
HR Agent Tizimini Sinovdan O'tkazish Skripti (Unit & Integration Tests)
"""

import sys
import os
import asyncio
from pathlib import Path

# Windows konsolida UTF-8 ni to'g'ri ko'rsatish
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Papka yo'lini qo'shish
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

import config
from services.database import (
    init_db,
    save_user,
    create_application,
    get_application_by_id,
    get_user_applications,
    update_application_status,
    get_statistics
)
from services.ai_agent import analyze_candidate_application
from utils.formatters import format_group_application_card, format_quick_cv_card
from utils.document_parser import extract_text_from_file

async def run_tests():
    print("=" * 60)
    print("🧪 1. Ma'lumotlar bazasi testlari...")
    await init_db()
    
    # User saqlash
    await save_user(123456789, "testuser", "Ali", "Valiyev")
    print("✅ Foydalanuvchi saqlandi.")
    
    # Sun'iy AI natijasi bilan ariza saqlash
    sample_ai_result = {
        "match_score": 88,
        "status": "MOS KELDI",
        "summary": "Nomzod Python Backend yo'nalishida mustahkam bilimga ega.",
        "strengths": [
            "FastAPI va PostgreSQL bilan 2 yillik tajriba",
            "Docker va Redis arxitekturasi bo'yicha amaliy ko'nikmalar",
            "Toza kod va test yozish madaniyati"
        ],
        "weaknesses": [
            "Kubernetes bo'yicha chuqur tajriba yo'q"
        ],
        "extracted_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis", "Git"],
        "experience_assessment": "2 yil tijoriy tajriba, Middle daraja",
        "hr_recommendation": "Texnik suhbatga chaqirish qat'iy tavsiya etiladi.",
        "interview_questions": [
            "PostgreSQL da indeksatsiya turlari va ulardan qachon foydalanish kerak?",
            "FastAPI da Dependency Injection qanday ishlaydi?",
            "Redis cache invalidation strategiyalarini tushuntirib bering."
        ]
    }
    
    app_id = await create_application(
        user_id=123456789,
        username="testuser",
        full_name="Ali Valiyev",
        phone="+998901234567",
        vacancy_key="python_backend",
        vacancy_title="🐍 Python Backend Dasturchi",
        experience_text="2 yil IT Park rezidenti bo'lgan kompaniyada backend ishlab chiqqanman.",
        salary_expectation="1200$",
        portfolio_url="https://github.com/testali",
        resume_file_id=None,
        resume_file_name="Ali_Valiyev_CV.pdf",
        resume_text="Python, Django, FastAPI, PostgreSQL, Redis, Docker bo'yicha tajribali dasturchi.",
        ai_result=sample_ai_result
    )
    print(f"✅ Ariza yaratildi! ID: #{app_id}")
    
    # Bazadan olish
    app = await get_application_by_id(app_id)
    assert app is not None, "Ariza bazadan topilmadi!"
    assert app["full_name"] == "Ali Valiyev"
    assert app["ai_score"] == 88
    print(f"✅ Bazadan ariza muvaffaqiyatli olindi: {app['full_name']} ({app['vacancy_title']})")
    
    # Holatni yangilash
    await update_application_status(app_id, "INVITED", "@HR_Manager", "Suhbat 28-avgust soat 15:00 da")
    app_updated = await get_application_by_id(app_id)
    assert app_updated["hr_status"] == "INVITED"
    print(f"✅ HR qarori yangilandi: {app_updated['hr_status']} ({app_updated['hr_decision_by']})")
    
    # Statistika
    stats = await get_statistics()
    print(f"✅ Statistika: {stats}")
    
    print("\n" + "=" * 60)
    print("🎨 2. Telegram xabar formati testi...")
    card_html = format_group_application_card(app_id, app, sample_ai_result)
    print("--- Guruh kartochkasi ko'rinishi ---")
    print(card_html)
    
    print("\n" + "=" * 60)
    print("🤖 3. OpenAI bilan jonli AI tahlil testi...")
    live_ai_result = await analyze_candidate_application(
        vacancy_title=config.VACANCIES["python_backend"]["title"],
        vacancy_requirements=config.VACANCIES["python_backend"]["requirements"],
        full_name="Sardor Rahim",
        phone="+998935557788",
        experience_text="1.5 yil Python FastAPI da mikroservislar yozganman, PostgreSQL va Celery ishlatganman.",
        salary_expectation="900$",
        portfolio_url="https://github.com/sardor-dev",
        resume_text="Tajriba: 1.5 yil Python dasturchi. Stack: Python, FastAPI, SQLite, PostgreSQL, Docker, Git."
    )
    print("✅ OpenAI Jonli Tahlil Natijasi:")
    print(f"  - Moslik: {live_ai_result.get('match_score')}% ({live_ai_result.get('status')})")
    print(f"  - Xulosa: {live_ai_result.get('summary')}")
    print(f"  - Kuchli tomonlar: {live_ai_result.get('strengths')}")
    print(f"  - Tavsiya: {live_ai_result.get('hr_recommendation')}")
    print(f"  - Suhbat savollari: {live_ai_result.get('interview_questions')}")

    print("\n" + "=" * 60)
    print("🎉 BARCHA TESTLAR MUVAFFAQIYATLI O'TDI!")

if __name__ == "__main__":
    asyncio.run(run_tests())
