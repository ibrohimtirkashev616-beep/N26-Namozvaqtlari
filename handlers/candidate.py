"""
Nomzodlar arizalarini qabul qilish va CV tahlili handleri
"""

import os
import html
import logging
from pathlib import Path
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import config
from states import ApplicationForm, QuickCVForm
from services.ai_agent import analyze_candidate_application
from services.database import create_application, update_application_group_message
from utils.document_parser import extract_text_from_file
from utils.formatters import format_group_application_card, format_quick_cv_card, get_status_badge
from keyboards.reply import (
    get_main_menu_keyboard,
    get_phone_request_keyboard,
    get_cancel_keyboard,
    get_skip_or_cancel_keyboard
)
from keyboards.inline import (
    get_vacancies_inline_keyboard,
    get_application_confirm_keyboard,
    get_hr_group_actions_keyboard,
    get_quick_cv_vacancy_keyboard
)

logger = logging.getLogger(__name__)
router = Router()


# =========================================================
# 1. TO'LIQ ARIZA TOPSHIRISH JARAYONI
# =========================================================

@router.message(F.text == "📝 Ariza topshirish")
async def start_application(message: Message, state: FSMContext):
    """Ariza topshirishni boshlash - Vakansiya tanlash."""
    await state.clear()
    await state.set_state(ApplicationForm.vacancy)
    
    text = (
        "💼 <b>Qaysi vakansiya bo'yicha ariza topshirmoqchisiz?</b>\n\n"
        "Quyidagi ro'yxatdan o'zingizga mos vakansiyani tanlang:"
    )
    await message.answer(text, reply_markup=get_vacancies_inline_keyboard(), parse_mode="HTML")


@router.callback_query(F.data.startswith("apply_vac:"), ApplicationForm.vacancy)
async def process_vacancy_selection(callback: CallbackQuery, state: FSMContext):
    """Vakansiya tanlandi -> Ism-familiya so'rash."""
    vac_key = callback.data.split(":", 1)[1]
    vac = config.VACANCIES.get(vac_key)
    
    if not vac:
        await callback.answer("Vakansiya topilmadi!", show_alert=True)
        return
        
    await state.update_data(vacancy_key=vac_key, vacancy_title=vac["title"], vacancy_requirements=vac["requirements"])
    await state.set_state(ApplicationForm.fullname)
    
    await callback.message.delete()
    await callback.message.answer(
        f"Tanlangan vakansiya: <b>{vac['title']}</b>\n\n"
        "👤 <b>1-qadam:</b> Iltimos, to'liq ism-familiyangizni kiriting (F.I.SH):",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(ApplicationForm.fullname, F.text)
async def process_fullname(message: Message, state: FSMContext):
    """Ism-familiya qabul qilindi -> Telefon raqam so'rash."""
    fullname = message.text.strip()
    if len(fullname) < 3:
        await message.answer("Iltimos, ism va familiyangizni to'liq kiriting:")
        return
        
    await state.update_data(fullname=fullname)
    await state.set_state(ApplicationForm.phone)
    
    await message.answer(
        "📱 <b>2-qadam:</b> Telefon raqamingizni kiriting yoki quyidagi tugma orqali yuboring:\n\n"
        "<i>Namuna: +998901234567</i>",
        reply_markup=get_phone_request_keyboard(),
        parse_mode="HTML"
    )


@router.message(ApplicationForm.phone, F.contact | F.text)
async def process_phone(message: Message, state: FSMContext):
    """Telefon raqam qabul qilindi -> Tajriba so'rash."""
    if message.contact:
        phone = message.contact.phone_number
        if not phone.startswith("+"):
            phone = "+" + phone
    else:
        phone = message.text.strip()
        
    await state.update_data(phone=phone)
    await state.set_state(ApplicationForm.experience)
    
    await message.answer(
        "⏳ <b>3-qadam:</b> Ushbu sohadagi ish tajribangiz haqida ma'lumot bering:\n\n"
        "<i>(Necha yil tajribaga egasiz, qaysi kompaniyalarda yoki loyihalarda ishlagansiz?)</i>",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )


@router.message(ApplicationForm.experience, F.text)
async def process_experience(message: Message, state: FSMContext):
    """Tajriba qabul qilindi -> Kutilayotgan maosh so'rash."""
    experience = message.text.strip()
    await state.update_data(experience=experience)
    await state.set_state(ApplicationForm.salary)
    
    await message.answer(
        "💰 <b>4-qadam:</b> Kutilayotgan oylik maoshingizni kiriting (USD yoki so'mda):\n\n"
        "<i>Namuna: 800$, 10 000 000 so'm yoki 'Kelishiladi'</i>",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )


@router.message(ApplicationForm.salary, F.text)
async def process_salary(message: Message, state: FSMContext):
    """Maosh qabul qilindi -> Portfolio/GitHub so'rash."""
    salary = message.text.strip()
    await state.update_data(salary=salary)
    await state.set_state(ApplicationForm.portfolio)
    
    await message.answer(
        "🔗 <b>5-qadam:</b> Portfolio, GitHub, LinkedIn yoki loyihalaringiz havolasini kiriting:\n\n"
        "<i>Agar mavjud bo'lmasa, '⏭ O'tkazib yuborish' tugmasini bosing.</i>",
        reply_markup=get_skip_or_cancel_keyboard(),
        parse_mode="HTML"
    )


@router.message(ApplicationForm.portfolio, F.text)
async def process_portfolio(message: Message, state: FSMContext):
    """Portfolio qabul qilindi -> Rezyume (CV) faylini so'rash."""
    text = message.text.strip()
    portfolio = "" if text == "⏭ O'tkazib yuborish" else text
    
    await state.update_data(portfolio=portfolio)
    await state.set_state(ApplicationForm.resume)
    
    await message.answer(
        "📄 <b>6-qadam:</b> Rezyumeingizni (CV) yuboring:\n\n"
        "📌 <b>Formatlar:</b> PDF yoki DOCX fayl ko'rinishida yuborishingiz tavsiya etiladi.\n"
        "<i>(Agar tayyor fayl bo'lmasa, rezyume matnini to'g'ridan-to'g'ri xabar sifatida yozib yuborishingiz ham mumkin)</i>",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )


@router.message(ApplicationForm.resume, F.document | F.text)
async def process_resume_upload(message: Message, state: FSMContext, bot: Bot):
    """Rezyume qabul qilindi -> Ma'lumotlarni tekshirish va tasdiqlash."""
    resume_file_id = None
    resume_file_name = None
    resume_text = ""
    
    if message.document:
        doc = message.document
        resume_file_id = doc.file_id
        resume_file_name = doc.file_name or "resume.pdf"
        
        # Faylni vaqtinchalik yuklab olib matnni ajratish
        try:
            file_info = await bot.get_file(doc.file_id)
            if file_info.file_path:
                ext = Path(resume_file_name).suffix or ".pdf"
                local_path = config.DOWNLOADS_DIR / f"res_{message.from_user.id}_{doc.file_unique_id}{ext}"
                await bot.download_file(file_info.file_path, local_path)
                
                # Matnni ajratish
                resume_text = extract_text_from_file(local_path)
                
                # Vaqtinchalik faylni o'chirish (joy tejash)
                try:
                    if local_path.exists():
                        local_path.unlink()
                except Exception:
                    pass
        except Exception as e:
            logger.error(f"Faylni yuklab olishda xatolik: {e}")
            resume_text = f"Fayl nomi: {resume_file_name}"
            
    elif message.text:
        resume_text = message.text.strip()
        
    await state.update_data(
        resume_file_id=resume_file_id,
        resume_file_name=resume_file_name,
        resume_text=resume_text
    )
    await state.set_state(ApplicationForm.confirm)
    
    # Kiritilgan ma'lumotlar xulosasini ko'rsatish
    data = await state.get_data()
    summary_msg = (
        "📋 <b>Arizangiz ma'lumotlari:</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"💼 <b>Vakansiya:</b> {data.get('vacancy_title')}\n"
        f"👤 <b>F.I.SH:</b> {html.escape(data.get('fullname', ''))}\n"
        f"📞 <b>Telefon:</b> {html.escape(data.get('phone', ''))}\n"
        f"⏳ <b>Tajriba:</b> {html.escape(data.get('experience', ''))}\n"
        f"💰 <b>Maosh:</b> {html.escape(data.get('salary', ''))}\n"
        f"🔗 <b>Portfolio:</b> {html.escape(data.get('portfolio') or 'Ko\'rsatilmagan')}\n"
        f"📄 <b>Rezyume:</b> {html.escape(data.get('resume_file_name') or 'Matn ko\'rinishida')}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "<i>Barcha ma'lumotlar to'g'ri bo'lsa, '🚀 Tasdiqlash va Yuborish' tugmasini bosing.</i>"
    )
    
    await message.answer(summary_msg, reply_markup=get_application_confirm_keyboard(), parse_mode="HTML")


@router.callback_query(F.data == "submit_app_confirm", ApplicationForm.confirm)
async def submit_application_final(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Nomzod arizasini AI orqali tahlil qilish, bazaga saqlash va HR guruhga yuborish."""
    data = await state.get_data()
    await state.clear()
    
    await callback.message.edit_text(
        "⏳ <b>Arizangiz qabul qilindi!</b>\n\n"
        "🤖 AI HR Agent ma'lumotlaringiz va rezyumeingizni tahlil qilmoqda...\n"
        "<i>Iltimos, bir necha soniya kuting...</i>",
        parse_mode="HTML"
    )
    
    # 1. AI Tahlilni ishga tushirish
    ai_result = await analyze_candidate_application(
        vacancy_title=data.get("vacancy_title", ""),
        vacancy_requirements=data.get("vacancy_requirements", ""),
        full_name=data.get("fullname", ""),
        phone=data.get("phone", ""),
        experience_text=data.get("experience", ""),
        salary_expectation=data.get("salary", ""),
        portfolio_url=data.get("portfolio", ""),
        resume_text=data.get("resume_text", "")
    )
    
    user = callback.from_user
    username = user.username or ""
    
    # 2. Bazaga saqlash
    app_id = await create_application(
        user_id=user.id,
        username=username,
        full_name=data.get("fullname", ""),
        phone=data.get("phone", ""),
        vacancy_key=data.get("vacancy_key", ""),
        vacancy_title=data.get("vacancy_title", ""),
        experience_text=data.get("experience", ""),
        salary_expectation=data.get("salary", ""),
        portfolio_url=data.get("portfolio", ""),
        resume_file_id=data.get("resume_file_id"),
        resume_file_name=data.get("resume_file_name"),
        resume_text=data.get("resume_text", ""),
        ai_result=ai_result
    )
    
    # 3. Guruhga yuboriladigan kartochkani tayyorlash
    app_dict = {
        "user_id": user.id,
        "username": username,
        "full_name": data.get("fullname", ""),
        "phone": data.get("phone", ""),
        "vacancy_title": data.get("vacancy_title", ""),
        "experience_text": data.get("experience", ""),
        "salary_expectation": data.get("salary", ""),
        "portfolio_url": data.get("portfolio", "")
    }
    
    group_card = format_group_application_card(app_id, app_dict, ai_result)
    action_kb = get_hr_group_actions_keyboard(app_id)
    
    # 4. Telegram Guruhga yuborish
    group_sent = False
    try:
        if data.get("resume_file_id"):
            # Fayl bilan birga yuborish
            # Agar matn 1024 belgidan oshsa, alohida xabar sifatida
            if len(group_card) <= 1024:
                sent_msg = await bot.send_document(
                    chat_id=config.HR_GROUP_ID,
                    document=data["resume_file_id"],
                    caption=group_card,
                    reply_markup=action_kb,
                    parse_mode="HTML"
                )
            else:
                # Avval hujjatni, keyin tahlil hisobotini yuborish
                await bot.send_document(
                    chat_id=config.HR_GROUP_ID,
                    document=data["resume_file_id"],
                    caption=f"📄 <b>Rezyume:</b> {data.get('fullname')} (#{app_id})",
                    parse_mode="HTML"
                )
                sent_msg = await bot.send_message(
                    chat_id=config.HR_GROUP_ID,
                    text=group_card,
                    reply_markup=action_kb,
                    parse_mode="HTML"
                )
            await update_application_group_message(app_id, sent_msg.message_id)
            group_sent = True
        else:
            sent_msg = await bot.send_message(
                chat_id=config.HR_GROUP_ID,
                text=group_card,
                reply_markup=action_kb,
                parse_mode="HTML"
            )
            await update_application_group_message(app_id, sent_msg.message_id)
            group_sent = True
            
    except Exception as e:
        logger.error(f"Guruhga xabar yuborishda xatolik ({config.HR_GROUP_ID}): {e}")
        # Guruhga yuborishda xatolik bo'lsa ham foydalanuvchiga muammosiz javob qaytaramiz
    
    # 5. Nomzodga yakuniy tasdiq xabarini yuborish
    score = ai_result.get("match_score", 0)
    ai_status = ai_result.get("status", "QISMAN MOS")
    status_badge = get_status_badge(ai_status)
    
    candidate_reply = (
        f"🎉 <b>Arizangiz muvaffaqiyatli qabul qilindi!</b>\n\n"
        f"📌 <b>Ariza raqami:</b> #{app_id}\n"
        f"💼 <b>Vakansiya:</b> {data.get('vacancy_title')}\n"
        f"🤖 <b>AI Dastlabki Tahlili:</b> {status_badge} ({score}%)\n\n"
        "✨ Arizangiz va rezyumeingiz HR jamoamizga yetkazildi. "
        "Mutaxassislarimiz arizangizni ko'rib chiqib, tez orada siz bilan bog'lanishadi.\n\n"
        "<i>Arizangiz holatini <b>'📊 Mening arizalarim'</b> bo'limida kuzatishingiz mumkin.</i>"
    )
    
    await callback.message.answer(candidate_reply, reply_markup=get_main_menu_keyboard(), parse_mode="HTML")
    await callback.answer()


# =========================================================
# 2. TEZKOR REZYUME (CV) TAHLILI
# =========================================================

@router.message(F.text == "⚡ Tezkor CV tahlili")
async def start_quick_cv(message: Message, state: FSMContext):
    """Tezkor CV tahlilini boshlash."""
    await state.clear()
    
    text = (
        "⚡ <b>Tezkor Rezyume (CV) Tahlili</b>\n\n"
        "Rezyumeingizni qaysi yo'nalish / vakansiya bo'yicha tahlil qilmoqchisiz?"
    )
    await message.answer(text, reply_markup=get_quick_cv_vacancy_keyboard(), parse_mode="HTML")


@router.callback_query(F.data.startswith("quick_vac:"))
async def process_quick_vac(callback: CallbackQuery, state: FSMContext):
    """Tezkor CV uchun vakansiya tanlandi -> Fayl so'rash."""
    vac_key = callback.data.split(":", 1)[1]
    vac = config.VACANCIES.get(vac_key)
    
    if not vac:
        await callback.answer("Vakansiya topilmadi!", show_alert=True)
        return
        
    await state.update_data(
        quick_vacancy_title=vac["title"],
        quick_vacancy_req=vac["requirements"]
    )
    await state.set_state(QuickCVForm.waiting_for_cv)
    
    await callback.message.delete()
    await callback.message.answer(
        f"Tanlangan yo'nalish: <b>{vac['title']}</b>\n\n"
        "📄 <b>Endi rezyumeingizni (PDF/DOCX fayl yoki matn ko'rinishida) yuboring:</b>\n"
        "<i>AI sizning CV ingizni ushbu yo'nalish talablariga mosligini to'liq tahlil qilib beradi.</i>",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(QuickCVForm.waiting_for_cv, F.document | F.text)
async def process_quick_cv_file(message: Message, state: FSMContext, bot: Bot):
    """CV faylini yoki matnini qabul qilib, OpenAI orqali tahlil qilish."""
    data = await state.get_data()
    await state.clear()
    
    wait_msg = await message.answer(
        "⏳ <b>Rezyumeingiz tahlil qilinmoqda...</b>\n"
        "<i>AI ko'nikmalaringiz, tajribangiz va kuchli tomonlaringizni baholamoqda. Iltimos, kuting...</i>",
        parse_mode="HTML"
    )
    
    resume_text = ""
    file_name = None
    
    if message.document:
        doc = message.document
        file_name = doc.file_name or "cv.pdf"
        try:
            file_info = await bot.get_file(doc.file_id)
            if file_info.file_path:
                ext = Path(file_name).suffix or ".pdf"
                local_path = config.DOWNLOADS_DIR / f"quick_{message.from_user.id}_{doc.file_unique_id}{ext}"
                await bot.download_file(file_info.file_path, local_path)
                resume_text = extract_text_from_file(local_path)
                try:
                    if local_path.exists():
                        local_path.unlink()
                except Exception:
                    pass
        except Exception as e:
            logger.error(f"Tezkor CV yuklashda xatolik: {e}")
            resume_text = f"Fayl: {file_name}"
    elif message.text:
        resume_text = message.text.strip()
        file_name = "Matnli CV"
        
    vac_title = data.get("quick_vacancy_title", "Umumiy dasturchi")
    vac_req = data.get("quick_vacancy_req", "Soha bo'yicha talablar")
    
    user = message.from_user
    user_name = user.full_name or user.first_name
    user_tag = f"@{user.username}" if user.username else f"ID: {user.id}"
    
    ai_result = await analyze_candidate_application(
        vacancy_title=vac_title,
        vacancy_requirements=vac_req,
        full_name=user_name,
        phone="Mavjud emas",
        experience_text="Rezyumedan aniqlansin",
        salary_expectation="Mavjud emas",
        portfolio_url="",
        resume_text=resume_text
    )
    
    card = format_quick_cv_card(user_name, user_tag, ai_result, file_name)
    
    await wait_msg.delete()
    await message.answer(card, reply_markup=get_main_menu_keyboard(), parse_mode="HTML")
