"""
Telegram xabarlarini chiroyli HTML formatida shakllantirish
"""

import html
from typing import Dict, Any, Optional

def get_status_badge(status: str) -> str:
    if status == "MOS KELDI":
        return "🟢 <b>MOS KELDI</b>"
    elif status == "QISMAN MOS":
        return "🟡 <b>QISMAN MOS</b>"
    else:
        return "🔴 <b>MOS KELMADI</b>"

def get_hr_status_badge(hr_status: str) -> str:
    badges = {
        "NEW": "🆕 <b>Yangi (Kutilmoqda)</b>",
        "INVITED": "✅ <b>Suhbatga chaqirildi</b>",
        "REJECTED": "❌ <b>Rad etildi</b>",
        "RESERVED": "⭐ <b>Zaxiraga olindi</b>"
    }
    return badges.get(hr_status, "🆕 <b>Yangi</b>")


def format_group_application_card(app_id: int, app_data: Dict[str, Any], ai_result: Dict[str, Any]) -> str:
    """Telegram guruhiga yuboriladigan to'liq va mukammal HR hisoboti."""
    
    score = ai_result.get("match_score", 0)
    ai_status = ai_result.get("status", "QISMAN MOS")
    status_badge = get_status_badge(ai_status)
    
    # Emojilar va foiz indikatori
    if score >= 75:
        score_bar = f"🟩🟩🟩🟩🟩 {score}%"
    elif score >= 50:
        score_bar = f"🟨🟨🟨⬜⬜ {score}%"
    else:
        score_bar = f"🟥⬜⬜⬜⬜ {score}%"

    full_name = html.escape(str(app_data.get("full_name", "")))
    username = app_data.get("username")
    user_tag = f"@{html.escape(username)}" if username else f"ID: {app_data.get('user_id')}"
    phone = html.escape(str(app_data.get("phone", "")))
    vacancy = html.escape(str(app_data.get("vacancy_title", "")))
    experience = html.escape(str(app_data.get("experience_text", "Ko'rsatilmagan")))
    salary = html.escape(str(app_data.get("salary_expectation", "Kelishiladi")))
    portfolio = html.escape(str(app_data.get("portfolio_url", "Mavjud emas")))
    
    summary = html.escape(ai_result.get("summary", ""))
    recommendation = html.escape(ai_result.get("hr_recommendation", ""))
    exp_assessment = html.escape(ai_result.get("experience_assessment", ""))
    
    # Kuchli tomonlar
    strengths_list = ai_result.get("strengths", [])
    strengths_text = "\n".join([f"  • {html.escape(s)}" for s in strengths_list]) if strengths_list else "  • Ko'rsatilmagan"
    
    # Kamchiliklar
    weaknesses_list = ai_result.get("weaknesses", [])
    weaknesses_text = "\n".join([f"  • {html.escape(w)}" for w in weaknesses_list]) if weaknesses_list else "  • Jiddiy kamchilik topilmadi"
    
    # Texnologiyalar
    skills = ai_result.get("extracted_skills", [])
    skills_text = ", ".join([f"<code>{html.escape(s)}</code>" for s in skills]) if skills else "Aniq ko'rsatilmagan"
    
    # Suhbat savollari
    questions = ai_result.get("interview_questions", [])
    questions_text = "\n".join([f"  {idx+1}. <i>{html.escape(q)}</i>" for idx, q in enumerate(questions)]) if questions else "  1. <i>Loyihalaringiz haqida batafsil ma'lumot bering.</i>"

    card = (
        f"📋 <b>YANGI ARIZA: #{app_id}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💼 <b>Vakansiya:</b> {vacancy}\n"
        f"👤 <b>Nomzod:</b> <b>{full_name}</b> ({user_tag})\n"
        f"📞 <b>Telefon:</b> <code>{phone}</code>\n"
        f"⏳ <b>Tajriba:</b> {experience}\n"
        f"💰 <b>Kutilayotgan maosh:</b> {salary}\n"
        f"🔗 <b>Portfolio/Havola:</b> {portfolio}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 <b>AI HR TAHLIL NATIJASI:</b>\n\n"
        f"📊 <b>Moslik darajasi:</b> {status_badge} | {score_bar}\n"
        f"🎯 <b>Tajriba bahosi:</b> {exp_assessment}\n"
        f"🛠 <b>Aniqlangan ko'nikmalar:</b> {skills_text}\n\n"
        f"📝 <b>Qisqacha xulosa:</b>\n{summary}\n\n"
        f"💪 <b>Kuchli tomonlari:</b>\n{strengths_text}\n\n"
        f"⚠️ <b>Kamchiliklari / Bo'shliqlar:</b>\n{weaknesses_text}\n\n"
        f"💡 <b>HR uchun tavsiya:</b>\n<b>{recommendation}</b>\n\n"
        f"❓ <b>Suhbat uchun tavsiya etilgan savollar:</b>\n{questions_text}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 <b>Holat:</b> 🆕 <i>Ko'rib chiqilmoqda</i>"
    )
    return card


def format_quick_cv_card(user_name: str, user_tag: str, ai_result: Dict[str, Any], file_name: Optional[str] = None) -> str:
    """Faqat CV yuborilgandagi tezkor tahlil xabari."""
    score = ai_result.get("match_score", 0)
    ai_status = ai_result.get("status", "QISMAN MOS")
    status_badge = get_status_badge(ai_status)
    
    summary = html.escape(ai_result.get("summary", ""))
    recommendation = html.escape(ai_result.get("hr_recommendation", ""))
    
    strengths_list = ai_result.get("strengths", [])
    strengths_text = "\n".join([f"  • {html.escape(s)}" for s in strengths_list]) if strengths_list else "  • Ko'rsatilmagan"
    
    weaknesses_list = ai_result.get("weaknesses", [])
    weaknesses_text = "\n".join([f"  • {html.escape(w)}" for w in weaknesses_list]) if weaknesses_list else "  • Jiddiy kamchilik topilmadi"
    
    skills = ai_result.get("extracted_skills", [])
    skills_text = ", ".join([f"<code>{html.escape(s)}</code>" for s in skills]) if skills else "Ko'rsatilmagan"

    card = (
        f"⚡ <b>TEZKOR REZYUME TAHLILI</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Foydalanuvchi:</b> {html.escape(user_name)} ({user_tag})\n"
        f"📄 <b>Fayl:</b> {html.escape(file_name or 'Matn ko\'rinishida')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 <b>Moslik bahosi:</b> {status_badge} ({score}%)\n"
        f"🛠 <b>Aniqlangan ko'nikmalar:</b> {skills_text}\n\n"
        f"📝 <b>Xulosa:</b>\n{summary}\n\n"
        f"💪 <b>Kuchli tomonlar:</b>\n{strengths_text}\n\n"
        f"⚠️ <b>Tavsiya va kamchiliklar:</b>\n{weaknesses_text}\n\n"
        f"💡 <b>Tavsiya:</b> {recommendation}"
    )
    return card
