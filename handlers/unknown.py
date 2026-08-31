# -*- coding: utf-8 -*-
"""
Noma'lum xabarlar va buyruqlar handleri
"""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.enums import ParseMode
import database
from texts import get_text
import keyboards

router = Router()


@router.message(F.text)
async def handle_unknown_message(message: Message):
    """Har qanday boshqa matnli xabarga xushmuomala va iliq javob."""
    user = await database.get_user(message.from_user.id)
    lang = user.get("language", "uz") if user else "uz"
    
    text = get_text("unknown_cmd", lang)
    reply_kb = keyboards.get_main_reply_keyboard(lang)
    await message.answer(text, reply_markup=reply_kb, parse_mode=ParseMode.HTML)
