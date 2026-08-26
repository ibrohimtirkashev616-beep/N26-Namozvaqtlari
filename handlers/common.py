"""
Umumiy buyruqlar va menyu handleri (/start, /help, ma'lumotlar)
"""

import html
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

import config
from services.database import save_user, get_user_applications
from keyboards.reply import get_main_menu_keyboard
from keyboards.inline import get_vacancy_info_keyboard, get_vacancies_inline_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Start buyrug'i handleri."""
    await state.clear()
    
    user = message.from_user
    if user:
        await save_user(user.id, user.username, user.first_name, user.last_name)
    
    welcome_text = (
        f"Assalomu alaykum, <b>{html.escape(user.first_name if user else 'Qadrli nomzod')}</b>! 👋\n\n"
        "🤖 <b>AI HR Agent</b> botiga xush kelibsiz!\n\n"
        "Ushbu bot orqali siz:\n"
        "• 📝 Kompaniyamizdagi bo'sh ish o'rinlariga ariza topshirishingiz\n"
        "• ⚡ Rezyumeingizni (CV) AI orqali tezkor tahlil qildirishingiz\n"
        "• 💼 Barcha ochiq vakansiyalar bilan tanishishingiz\n"
        "• 📊 Topshirgan arizalaringiz holatini kuzatib borishingiz mumkin.\n\n"
        "<i>Kerakli bo'limni tanlash uchun quyidagi tugmalardan foydalaning:</i>"
    )
    await message.answer(welcome_text, reply_markup=get_main_menu_keyboard(), parse_mode="HTML")


@router.message(F.text == "❌ Bekor qilish")
@router.callback_query(F.data == "cancel_application")
async def handle_cancel(event: Message | CallbackQuery, state: FSMContext):
    """Jarayonni bekor qilish."""
    await state.clear()
    cancel_text = "❌ Jarayon bekor qilindi. Asosiy menyudasiz."
    
    if isinstance(event, CallbackQuery):
        await event.answer("Bekor qilindi")
        if event.message:
            await event.message.answer(cancel_text, reply_markup=get_main_menu_keyboard())
    else:
        await event.answer(cancel_text, reply_markup=get_main_menu_keyboard())


@router.message(F.text == "ℹ️ Bot haqida / Yordam")
@router.message(Command("help"))
async def cmd_help(message: Message):
    """Yordam va bot haqida ma'lumot."""
    help_text = (
        "ℹ️ <b>AI HR Agent Boti Haqida</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Ushbu bot sun'iy intellekt (OpenAI GPT) yordamida nomzodlarning rezyumelarini tahlil qiladi, "
        "moslik darajasini aniqlaydi va arizalarni HR jamoasiga to'liq hisobot ko'rinishida yetkazadi.\n\n"
        "📌 <b>Qanday foydalaniladi?</b>\n"
        "1. <b>'📝 Ariza topshirish'</b> tugmasini bosing.\n"
        "2. Vakansiyani tanlang va kerakli ma'lumotlarni to'ldiring.\n"
        "3. Rezyumeingizni (PDF/DOCX) yuboring.\n"
        "4. AI arizangizni tahlil qilib, HR jamoasiga yuboradi.\n\n"
        "⚡ <b>'Tezkor CV tahlili'</b> orqali o'z rezyumeingizni mustaqil tekshirib olishingiz mumkin."
    )
    await message.answer(help_text, reply_markup=get_main_menu_keyboard(), parse_mode="HTML")


@router.message(F.text == "💼 Bo'sh ish o'rinlari")
async def show_vacancies_menu(message: Message):
    """Bo'sh ish o'rinlari ro'yxati."""
    text = (
        "💼 <b>Mavjud Bo'sh Ish O'rinlari</b>\n\n"
        "Batafsil ma'lumot olish uchun quyidagi vakansiyalardan birini tanlang:"
    )
    await message.answer(text, reply_markup=get_vacancy_info_keyboard(), parse_mode="HTML")


@router.callback_query(F.data.startswith("info_vac:"))
async def show_vacancy_details(callback: CallbackQuery):
    """Tanlangan vakansiya haqida batafsil ma'lumot."""
    vac_key = callback.data.split(":", 1)[1]
    vac = config.VACANCIES.get(vac_key)
    
    if not vac:
        await callback.answer("Vakansiya topilmadi!", show_alert=True)
        return
        
    text = (
        f"<b>{vac['title']}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 <b>Tavsif:</b> {vac['description']}\n\n"
        f"📋 <b>Talablar:</b>\n{vac['requirements'].strip()}\n\n"
        f"<i>Ushbu vakansiyaga ariza topshirish uchun '📝 Ariza topshirish' tugmasidan foydalaning.</i>"
    )
    await callback.message.edit_text(text, reply_markup=get_vacancy_info_keyboard(), parse_mode="HTML")
    await callback.answer()


@router.message(F.text == "📊 Mening arizalarim")
async def show_my_applications(message: Message):
    """Foydalanuvchining topshirgan arizalari holati."""
    user_id = message.from_user.id
    apps = await get_user_applications(user_id)
    
    if not apps:
        await message.answer(
            "Siz hali birorta ham ariza topshirmagansiz.\n"
            "Ariza topshirish uchun <b>'📝 Ariza topshirish'</b> tugmasini bosing.",
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML"
        )
        return
        
    response = ["📊 <b>Sizning topshirgan arizalaringiz:</b>\n"]
    
    status_emojis = {
        "NEW": "🆕 Ko'rib chiqilmoqda",
        "INVITED": "✅ Suhbatga chaqirildingiz",
        "REJECTED": "❌ Rad etilgan",
        "RESERVED": "⭐ Zaxirada"
    }
    
    for app in apps[:5]:
        hr_status_text = status_emojis.get(app.get("hr_status"), "Ko'rib chiqilmoqda")
        score = app.get("ai_score", 0)
        vac_title = app.get("vacancy_title", "Vakansiya")
        date_str = app.get("created_at", "")[:10]
        
        response.append(
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📌 <b>Ariza #{app['id']}</b> — {vac_title}\n"
            f"📅 Sana: {date_str}\n"
            f"🤖 AI Moslik: <b>{score}%</b>\n"
            f"📌 Holat: <b>{hr_status_text}</b>\n"
        )
        
    await message.answer("\n".join(response), reply_markup=get_main_menu_keyboard(), parse_mode="HTML")
