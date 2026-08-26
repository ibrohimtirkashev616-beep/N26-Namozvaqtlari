"""
HR Admin va Guruh boshqaruvi handleri
"""

import html
import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

import config
from states import AdminCustomMessageForm
from services.database import (
    get_application_by_id,
    update_application_status,
    get_statistics
)

logger = logging.getLogger(__name__)
router = Router()


# =========================================================
# 1. HR GURUHIDAGI HARAKATLAR (CALLBACKS)
# =========================================================

@router.callback_query(F.data.startswith("hr_act:"))
async def handle_hr_action(callback: CallbackQuery, bot: Bot, state: FSMContext):
    """Guruhdagi kartochka tugmalari bosilganda ishlaydi."""
    parts = callback.data.split(":")
    if len(parts) != 3:
        await callback.answer("Noto'g'ri buyruq!", show_alert=True)
        return
        
    action, app_id_str = parts[1], parts[2]
    try:
        app_id = int(app_id_str)
    except ValueError:
        await callback.answer("Ariza ID xato!", show_alert=True)
        return
        
    app = await get_application_by_id(app_id)
    if not app:
        await callback.answer("Ariza ma'lumotlar bazasidan topilmadi!", show_alert=True)
        return
        
    admin_user = callback.from_user
    admin_name = f"@{admin_user.username}" if admin_user.username else (admin_user.full_name or admin_user.first_name)
    
    cand_user_id = app.get("user_id")
    cand_name = html.escape(str(app.get("full_name", "Nomzod")))
    vac_title = html.escape(str(app.get("vacancy_title", "Vakansiya")))
    
    # -----------------------------------------------------
    # A) SUHBATGA CHAQIRISH
    # -----------------------------------------------------
    if action == "invite":
        await update_application_status(app_id, "INVITED", admin_name)
        
        # Guruhdagi xabarni yangilash
        try:
            status_note = f"\n\n━━━━━━━━━━━━━━━━━━━━\n📌 <b>HR QARORI:</b> ✅ <b>Suhbatga chaqirildi</b> ({admin_name} tomonidan)"
            if callback.message.caption:
                await callback.message.edit_caption(
                    caption=callback.message.caption + status_note,
                    reply_markup=None,
                    parse_mode="HTML"
                )
            elif callback.message.text:
                await callback.message.edit_text(
                    text=callback.message.text + status_note,
                    reply_markup=None,
                    parse_mode="HTML"
                )
        except Exception as e:
            logger.error(f"Guruh xabarini tahrirlashda xatolik: {e}")
            
        # Nomzodga xabar yuborish
        try:
            invite_text = (
                f"🎉 <b>Ajoyib yangilik, {cand_name}!</b>\n\n"
                f"Sizning <b>{vac_title}</b> bo'yicha topshirgan arizangiz HR bo'limimiz tomonidan ko'rib chiqildi "
                f"va siz <b>suhbatga (intervyu)</b> taklif qilindingiz!\n\n"
                f"Tez orada mas'ul xodimimiz siz bilan bog'lanib, suhbat vaqti va formatini belgilaydi.\n\n"
                f"<i>Omad tilaymiz! ✨</i>"
            )
            await bot.send_message(chat_id=cand_user_id, text=invite_text, parse_mode="HTML")
            await callback.answer(f"✅ Nomzod ({cand_name}) suhbatga chaqirildi va xabardor qilindi!", show_alert=True)
        except Exception as e:
            logger.error(f"Nomzodga xabar yuborishda xatolik: {e}")
            await callback.answer(f"✅ Qabul qilindi, lekin nomzodga xabar yuborib bo'lmadi (botni bloklagan bo'lishi mumkin).", show_alert=True)

    # -----------------------------------------------------
    # B) RAD ETISH
    # -----------------------------------------------------
    elif action == "reject":
        await update_application_status(app_id, "REJECTED", admin_name)
        
        try:
            status_note = f"\n\n━━━━━━━━━━━━━━━━━━━━\n📌 <b>HR QARORI:</b> ❌ <b>Rad etildi</b> ({admin_name} tomonidan)"
            if callback.message.caption:
                await callback.message.edit_caption(
                    caption=callback.message.caption + status_note,
                    reply_markup=None,
                    parse_mode="HTML"
                )
            elif callback.message.text:
                await callback.message.edit_text(
                    text=callback.message.text + status_note,
                    reply_markup=None,
                    parse_mode="HTML"
                )
        except Exception as e:
            logger.error(f"Guruh xabarini tahrirlashda xatolik: {e}")
            
        try:
            reject_text = (
                f"Hurmatli <b>{cand_name}</b>,\n\n"
                f"Kompaniyamizning <b>{vac_title}</b> vakansiyasiga qiziqish bildirganingiz uchun minnatdorchilik bildiramiz.\n\n"
                f"Arizangiz va rezyumeingiz diqqat bilan o'rganib chiqildi. Afsuski, ayni damda ushbu pozitsiya talablariga mosroq bo'lgan boshqa nomzod bilan jarayonni davom ettirishga qaror qildik.\n\n"
                f"Sizning rezyumeingiz bizning bazamizda saqlanib qoladi va kelgusida mos vakansiyalar paydo bo'lsa, albatta siz bilan bog'lanamiz.\n\n"
                f"<i>Kelgusi kasbiy faoliyatingizda ulkan muvaffaqiyatlar tilaymiz!</i>"
            )
            await bot.send_message(chat_id=cand_user_id, text=reject_text, parse_mode="HTML")
            await callback.answer(f"❌ Nomzod arizasi rad etildi va xabarnoma yuborildi.", show_alert=True)
        except Exception as e:
            logger.error(f"Nomzodga xabar yuborishda xatolik: {e}")
            await callback.answer(f"❌ Rad etildi (nomzodga yetkazilmadi).", show_alert=True)

    # -----------------------------------------------------
    # C) ZAXIRAGA OLISH
    # -----------------------------------------------------
    elif action == "reserve":
        await update_application_status(app_id, "RESERVED", admin_name)
        
        try:
            status_note = f"\n\n━━━━━━━━━━━━━━━━━━━━\n📌 <b>HR QARORI:</b> ⭐ <b>Zaxiraga olindi</b> ({admin_name} tomonidan)"
            if callback.message.caption:
                await callback.message.edit_caption(
                    caption=callback.message.caption + status_note,
                    reply_markup=None,
                    parse_mode="HTML"
                )
            elif callback.message.text:
                await callback.message.edit_text(
                    text=callback.message.text + status_note,
                    reply_markup=None,
                    parse_mode="HTML"
                )
        except Exception as e:
            logger.error(f"Guruh xabarini tahrirlashda xatolik: {e}")
            
        try:
            reserve_text = (
                f"Hurmatli <b>{cand_name}</b>,\n\n"
                f"Sizning <b>{vac_title}</b> vakansiyasi bo'yicha topshirgan arizangiz ko'rib chiqildi va <b>zaxira kadrlar ro'yxatiga (Talent Pool)</b> kiritildi.\n\n"
                f"Yangi loyihalar yoki imkoniyatlar ochilishi bilan siz bilan birinchi navbatda bog'lanamiz!"
            )
            await bot.send_message(chat_id=cand_user_id, text=reserve_text, parse_mode="HTML")
            await callback.answer(f"⭐ Nomzod zaxiraga olindi.", show_alert=True)
        except Exception as e:
            logger.error(f"Nomzodga xabar yuborishda xatolik: {e}")
            await callback.answer("⭐ Nomzod zaxiraga olindi.", show_alert=True)

    # -----------------------------------------------------
    # D) XUSUSIY XABAR YUBORISH
    # -----------------------------------------------------
    elif action == "msg":
        await state.update_data(target_user_id=cand_user_id, target_app_id=app_id, cand_name=cand_name)
        await state.set_state(AdminCustomMessageForm.waiting_for_message)
        
        await callback.answer("Xabarni botning shaxsiy chatiga yozing.", show_alert=True)
        try:
            await bot.send_message(
                chat_id=admin_user.id,
                text=f"💬 <b>Nomzodga ({cand_name}) xabar yuborish:</b>\n\n"
                     f"Iltimos, nomzodga yubormoqchi bo'lgan xabaringizni yozing (masalan, suhbat vaqti yoki test topshirig'i havola):\n\n"
                     f"<i>Bekor qilish uchun /cancel deb yozing.</i>",
                parse_mode="HTML"
            )
        except Exception:
            pass


@router.message(AdminCustomMessageForm.waiting_for_message, F.text)
async def process_admin_custom_message(message: Message, state: FSMContext, bot: Bot):
    """Admin kiritgan xususiy xabarni nomzodga yetkazish."""
    if message.text.strip().lower() in ["/cancel", "bekor qilish"]:
        await state.clear()
        await message.answer("❌ Xabar yuborish bekor qilindi.")
        return
        
    data = await state.get_data()
    await state.clear()
    
    target_user_id = data.get("target_user_id")
    cand_name = data.get("cand_name", "Nomzod")
    
    if not target_user_id:
        await message.answer("Xatolik: Nomzod ID si topilmadi.")
        return
        
    try:
        cand_msg = (
            f"📩 <b>HR Bo'limidan xabar:</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{html.escape(message.text)}\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        await bot.send_message(chat_id=target_user_id, text=cand_msg, parse_mode="HTML")
        await message.answer(f"✅ Xabaringiz nomzodga ({cand_name}) muvaffaqiyatli yetkazildi!")
    except Exception as e:
        logger.error(f"Xabar yuborishda xatolik: {e}")
        await message.answer(f"❌ Xabar yuborib bo'lmadi: {e}")


# =========================================================
# 2. HR STATISTIKASI BUYRUG'I
# =========================================================

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """HR bot statistikasi."""
    stats = await get_statistics()
    
    total = stats.get("total_apps", 0)
    qualified = stats.get("qualified", 0)
    partially = stats.get("partially_qualified", 0)
    rejected_ai = stats.get("rejected_ai", 0)
    invited = stats.get("invited", 0)
    rejected_hr = stats.get("rejected_hr", 0)
    users_count = stats.get("total_users", 0)
    
    qual_percent = round((qualified / total * 100), 1) if total > 0 else 0
    
    text = (
        "📊 <b>AI HR Agent Statistikasi</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 <b>Bot foydalanuvchilari:</b> {users_count} ta\n"
        f"📝 <b>Jami topshirilgan arizalar:</b> {total} ta\n\n"
        "🤖 <b>AI Tahlil Natijalari:</b>\n"
        f"  🟢 Mos kelgan (>=75%): <b>{qualified} ta</b> ({qual_percent}%)\n"
        f"  🟡 Qisman mos (50-74%): <b>{partially} ta</b>\n"
        f"  🔴 Mos kelmagan (<50%): <b>{rejected_ai} ta</b>\n\n"
        "👔 <b>HR Mutaxassislari Qarorlari:</b>\n"
        f"  ✅ Suhbatga chaqirilgan: <b>{invited} ta</b>\n"
        f"  ❌ Rad etilgan: <b>{rejected_hr} ta</b>\n"
        f"  🆕 Ko'rib chiqilmoqda: <b>{total - invited - rejected_hr} ta</b>\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )
    await message.answer(text, parse_mode="HTML")
