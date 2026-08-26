"""
OpenAI asosidagi HR tahlil agenti
"""

import json
import logging
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
import config

logger = logging.getLogger(__name__)

# AsyncOpenAI mijozi
_client: Optional[AsyncOpenAI] = None

def get_openai_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
    return _client


SYSTEM_PROMPT = """Siz professional IT va HR tahlilchi (AI HR Recruiter) mutaxassisisiz.
Vazifangiz: Nomzodning ma'lumotlari va rezyumesini (CV) berilgan vakansiya talablariga mosligini xolisona, chuqur va aniq tahlil qilish.

Tahlil davomida quyidagilarni aniqlang:
1. "match_score": 0 dan 100 gacha bo'lgan raqam (butun son). Nomzodning vakansiya talablariga qanchalik mos kelish foizi.
2. "status": Moslik holati:
   - "MOS KELDI" (agar match_score >= 75 bo'lsa)
   - "QISMAN MOS" (agar match_score 50 dan 74 gacha bo'lsa)
   - "MOS KELMADI" (agar match_score < 50 bo'lsa)
3. "summary": Nomzod haqida 2-3 jumlalik qisqacha xulosa (o'zbek tilida).
4. "strengths": Nomzodning kuchli tomonlari (ro'yxat, har biri qisqa punkt).
5. "weaknesses": Nomzodning kamchiliklari, yetishmayotgan ko'nikmalari yoki tajriba bo'shliqlari (ro'yxat).
6. "extracted_skills": Nomzod ega bo'lgan asosiy texnologiya va ko'nikmalar ro'yxati (masalan: ["Python", "Django", "PostgreSQL", "Docker"]).
7. "experience_assessment": Nomzodning tajribasi bo'yicha baho (masalan: "1.5 yil tijoriy tajriba, Junior+/Middle daraja").
8. "hr_recommendation": HR mutaxassisi uchun aniq tavsiya (masalan: "Texnik suhbatga chaqirish tavsiya etiladi", "Test topshirig'i berish maqsadga muvofiq", "Ushbu vakansiyaga mos emas, rad etish tavsiya etiladi").
9. "interview_questions": Suhbatda nomzodga berish tavsiya etiladigan 3 ta savol (nomzodning rezyumesi va tajribasiga moslashtirilgan holda).

Javobni FAQAT quyidagi JSON formatida qaytaring:
{
    "match_score": 85,
    "status": "MOS KELDI",
    "summary": "...",
    "strengths": ["...", "..."],
    "weaknesses": ["..."],
    "extracted_skills": ["...", "..."],
    "experience_assessment": "...",
    "hr_recommendation": "...",
    "interview_questions": ["...", "...", "..."]
}
"""


async def analyze_candidate_application(
    vacancy_title: str,
    vacancy_requirements: str,
    full_name: str,
    phone: str,
    experience_text: str,
    salary_expectation: str,
    portfolio_url: str,
    resume_text: str = ""
) -> Dict[str, Any]:
    """Nomzodning arizasi va CV matnini OpenAI orqali tahlil qiladi."""
    
    # Matnni qisqartirish (keraksiz token sarfini oldini olish)
    cleaned_resume = resume_text.strip()[:10000] if resume_text else "Rezyume matni biriktirilmagan (faqat anketadagi ma'lumotlar mavjud)."
    
    user_prompt = f"""
--- VAKANSIYA MA'LUMOTLARI ---
Vakansiya: {vacancy_title}
Talablar:
{vacancy_requirements}

--- NOMZODNING ANKETA MA'LUMOTLARI ---
Ism-familiya: {full_name}
Telefon: {phone}
Kiritilgan tajriba: {experience_text}
Kutilayotgan maosh: {salary_expectation}
Portfolio/GitHub/Havola: {portfolio_url or "Ko'rsatilmagan"}

--- NOMZODNING REZYUME (CV) MATNI ---
{cleaned_resume}
"""

    try:
        client = get_openai_client()
        response = await client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        raw_content = response.choices[0].message.content
        data = json.loads(raw_content)
        
        # Qiymatlarni tekshirish va tozalash
        match_score = int(data.get("match_score", 50))
        if match_score < 0:
            match_score = 0
        elif match_score > 100:
            match_score = 100
            
        if match_score >= 75:
            status = "MOS KELDI"
        elif match_score >= 50:
            status = "QISMAN MOS"
        else:
            status = "MOS KELMADI"
            
        return {
            "match_score": match_score,
            "status": status,
            "summary": data.get("summary", "Nomzod arizasi ko'rib chiqildi."),
            "strengths": data.get("strengths", []),
            "weaknesses": data.get("weaknesses", []),
            "extracted_skills": data.get("extracted_skills", []),
            "experience_assessment": data.get("experience_assessment", "Ma'lumot kam"),
            "hr_recommendation": data.get("hr_recommendation", "HR tomonidan ko'rib chiqilsin"),
            "interview_questions": data.get("interview_questions", [])
        }
        
    except Exception as e:
        logger.error(f"OpenAI tahlilida xatolik: {e}")
        # Fallback tahlil
        return {
            "match_score": 60,
            "status": "QISMAN MOS",
            "summary": "AI tahlilida vaqtinchalik uzilish yuz berdi, lekin ariza to'liq saqlandi.",
            "strengths": ["Ariza muvaffaqiyatli topshirildi", "Hujjatlar biriktirilgan"],
            "weaknesses": ["Avtomatik tahlil qilinmadi (qo'lda ko'rish tavsiya etiladi)"],
            "extracted_skills": [],
            "experience_assessment": experience_text or "Ko'rsatilmagan",
            "hr_recommendation": "HR mutaxassisi tomonidan to'g'ridan-to'g'ri o'rganib chiqilsin.",
            "interview_questions": [
                "Loyiha tajribangiz haqida so'zlab bering.",
                "Qaysi texnologiyalar bilan ko'proq ishlagansiz?",
                "Kompaniyamizda ishlashdan maqsadingiz nima?"
            ]
        }
