# -*- coding: utf-8 -*-
"""
Bot xabarlari, shablonlari va tarjimalari (O'zbek, Rus va Ingliz tillari)
Iliq, samimiy va hurmatli insoniy ohangda.
"""

import random
from typing import Dict, Any, List

MONTHS = {
    "uz": {
        1: "yanvar", 2: "fevral", 3: "mart", 4: "aprel", 5: "may", 6: "iyun",
        7: "iyul", 8: "avgust", 9: "sentabr", 10: "oktabr", 11: "noyabr", 12: "dekabr"
    },
    "ru": {
        1: "января", 2: "февраля", 3: "марта", 4: "апреля", 5: "мая", 6: "июня",
        7: "июля", 8: "августа", 9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
    },
    "en": {
        1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
        7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"
    }
}

WEEKDAYS = {
    "uz": ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"],
    "ru": ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"],
    "en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
}

PRAYER_NAMES = {
    "uz": {
        "fajr": "Bomdod",
        "sunrise": "Quyosh",
        "dhuhr": "Peshin",
        "asr": "Asr",
        "maghrib": "Shom",
        "isha": "Xufton"
    },
    "ru": {
        "fajr": "Фаджр (Бомдод)",
        "sunrise": "Восход",
        "dhuhr": "Зухр (Пешин)",
        "asr": "Аср",
        "maghrib": "Магриб (Шом)",
        "isha": "Иша (Хуфтон)"
    },
    "en": {
        "fajr": "Fajr (Dawn)",
        "sunrise": "Sunrise",
        "dhuhr": "Dhuhr (Noon)",
        "asr": "Asr (Afternoon)",
        "maghrib": "Maghrib (Sunset)",
        "isha": "Isha (Night)"
    }
}

PRAYER_SHORT_NAMES = {
    "uz": {
        "fajr": "Bomdod",
        "sunrise": "Quyosh",
        "dhuhr": "Peshin",
        "asr": "Asr",
        "maghrib": "Shom",
        "isha": "Xufton"
    },
    "ru": {
        "fajr": "Фаджр",
        "sunrise": "Восход",
        "dhuhr": "Зухр",
        "asr": "Аср",
        "maghrib": "Магриб",
        "isha": "Иша"
    },
    "en": {
        "fajr": "Fajr",
        "sunrise": "Sunrise",
        "dhuhr": "Dhuhr",
        "asr": "Asr",
        "maghrib": "Maghrib",
        "isha": "Isha"
    }
}

# Eslatmalar uchun iliq, samimiy va diniy duolar ro'yxati (statik)
PRAYER_BLESSINGS = {
    "uz": [
        "Alloh ibodatingizni qabul qilsin 🤲",
        "Inshaalloh, namozingiz qabul bo'lsin 🤲",
        "Yaxshi namoz o'qing 🤲",
        "Alloh yor bo'lsin 🤲"
    ],
    "ru": [
        "Да примет Аллах ваши молитвы 🤲",
        "Иншааллах, пусть ваш намаз будет принят 🤲",
        "Благословенного и искреннего вам намаза 🤲",
        "Пусть Аллах пребудет с вами 🤲"
    ],
    "en": [
        "May Allah accept your prayers 🤲",
        "Insha'Allah, may your prayer be accepted 🤲",
        "Have a blessed and peaceful prayer 🤲",
        "May Allah be with you 🤲"
    ]
}


def get_random_blessing(lang: str = "uz") -> str:
    """Tasodifiy bitta iliq duo jumlasini tanlash."""
    blessings = PRAYER_BLESSINGS.get(lang) or PRAYER_BLESSINGS["uz"]
    return random.choice(blessings)


TEXTS = {
    "start_welcome": {
        "uz": (
            "🕌 Assalomu alaykum va rahmatulloh!\n\n"
            "Namoz vaqtlari va azon eslatma botiga xush kelibsiz.\n"
            "Sizga xizmat qilishdan xursandmiz. Qaysi tilda davom etishni ma'qul ko'rasiz? 😊"
        ),
        "ru": (
            "🕌 Здравствуйте и добро пожаловать!\n\n"
            "Рады приветствовать вас в боте времени намаза и напоминаний.\n"
            "Пожалуйста, выберите удобный для вас язык общения: 😊"
        ),
        "en": (
            "🕌 Peace be upon you and welcome!\n\n"
            "Welcome to the Prayer Times & Adhan Reminder Bot.\n"
            "We are happy to assist you. Please choose your preferred language: 😊"
        )
    },
    "choose_region": {
        "uz": (
            "📍 Qaysi viloyat yoki shahardasiz?\n\n"
            "Namoz vaqtlarini aniq va to'g'ri ko'rsatishimiz uchun hududingizni tanlang:"
        ),
        "ru": (
            "📍 В каком регионе или городе вы находитесь?\n\n"
            "Выберите ваш регион для точного отображения времени намаза:"
        ),
        "en": (
            "📍 Which region or city are you in?\n\n"
            "Please select your region so we can display accurate prayer times:"
        )
    },
    "reg_success": {
        "uz": (
            "✨ <b>Ajoyib, barchasi tayyor!</b>\n\n"
            "📍 Hudud: <b>{region}</b>\n"
            "🗣 Til: <b>{language}</b>\n\n"
            "Endi quyidagi asosiy menyudan bemalol foydalanishingiz mumkin 👇"
        ),
        "ru": (
            "✨ <b>Отлично, всё готово!</b>\n\n"
            "📍 Регион: <b>{region}</b>\n"
            "🗣 Язык: <b>{language}</b>\n\n"
            "Теперь вы можете удобно пользоваться главным меню ниже 👇"
        ),
        "en": (
            "✨ <b>Great, everything is set!</b>\n\n"
            "📍 Region: <b>{region}</b>\n"
            "🗣 Language: <b>{language}</b>\n\n"
            "You can now explore the main menu below 👇"
        )
    },
    "btn_today": {
        "uz": "🕌 Bugungi namoz vaqtlari",
        "ru": "🕌 Время намаза на сегодня",
        "en": "🕌 Today's prayer times"
    },
    "btn_week": {
        "uz": "📅 Haftalik jadval",
        "ru": "📅 Недельное расписание",
        "en": "📅 Weekly schedule"
    },
    "btn_reminders": {
        "uz": "🔔 Eslatma sozlamalari",
        "ru": "🔔 Настройки напоминаний",
        "en": "🔔 Reminder settings"
    },
    "btn_settings": {
        "uz": "⚙️ Sozlamalar",
        "ru": "⚙️ Настройки",
        "en": "⚙️ Settings"
    },
    "today_template": {
        "uz": (
            "🕌 <b>{hudud}</b> — {sana} ({hafta_kuni})\n\n"
            "🌅 Bomdod       <code>{fajr}</code>\n"
            "🌄 Quyosh       <code>{sunrise}</code>\n"
            "☀️ Peshin       <code>{dhuhr}</code>\n"
            "🌤 Asr           <code>{asr}</code>\n"
            "🌇 Shom          <code>{maghrib}</code>\n"
            "🌙 Xufton        <code>{isha}</code>\n\n"
            "━━━━━━━━━━━━━━━\n"
            "⏳ Keyingi namoz: <b>{next_name} ({next_time})</b> — {time_left}dan so'ng"
        ),
        "ru": (
            "🕌 <b>{hudud}</b> — {sana} ({hafta_kuni})\n\n"
            "🌅 Фаджр (Бомдод)  <code>{fajr}</code>\n"
            "🌄 Восход           <code>{sunrise}</code>\n"
            "☀️ Зухр (Пешин)     <code>{dhuhr}</code>\n"
            "🌤 Аср              <code>{asr}</code>\n"
            "🌇 Магриб (Шом)     <code>{maghrib}</code>\n"
            "🌙 Иша (Хуфтон)     <code>{isha}</code>\n\n"
            "━━━━━━━━━━━━━━━\n"
            "⏳ Следующий намаз: <b>{next_name} ({next_time})</b> — через {time_left}"
        ),
        "en": (
            "🕌 <b>{hudud}</b> — {sana} ({hafta_kuni})\n\n"
            "🌅 Fajr (Dawn)       <code>{fajr}</code>\n"
            "🌄 Sunrise           <code>{sunrise}</code>\n"
            "☀️ Dhuhr (Noon)      <code>{dhuhr}</code>\n"
            "🌤 Asr (Afternoon)   <code>{asr}</code>\n"
            "🌇 Maghrib (Sunset)  <code>{maghrib}</code>\n"
            "🌙 Isha (Night)      <code>{isha}</code>\n\n"
            "━━━━━━━━━━━━━━━\n"
            "⏳ Next prayer: <b>{next_name} ({next_time})</b> — in {time_left}"
        )
    },
    "tomorrow_template": {
        "uz": (
            "🕌 <b>{hudud}</b> — {sana} ({hafta_kuni}) [Ertangi kun]\n\n"
            "🌅 Bomdod       <code>{fajr}</code>\n"
            "🌄 Quyosh       <code>{sunrise}</code>\n"
            "☀️ Peshin       <code>{dhuhr}</code>\n"
            "🌤 Asr           <code>{asr}</code>\n"
            "🌇 Shom          <code>{maghrib}</code>\n"
            "🌙 Xufton        <code>{isha}</code>"
        ),
        "ru": (
            "🕌 <b>{hudud}</b> — {sana} ({hafta_kuni}) [Завтра]\n\n"
            "🌅 Фаджр (Бомдод)  <code>{fajr}</code>\n"
            "🌄 Восход           <code>{sunrise}</code>\n"
            "☀️ Зухр (Пешин)     <code>{dhuhr}</code>\n"
            "🌤 Аср              <code>{asr}</code>\n"
            "🌇 Магриб (Шом)     <code>{maghrib}</code>\n"
            "🌙 Иша (Хуфтон)     <code>{isha}</code>"
        ),
        "en": (
            "🕌 <b>{hudud}</b> — {sana} ({hafta_kuni}) [Tomorrow]\n\n"
            "🌅 Fajr (Dawn)       <code>{fajr}</code>\n"
            "🌄 Sunrise           <code>{sunrise}</code>\n"
            "☀️ Dhuhr (Noon)      <code>{dhuhr}</code>\n"
            "🌤 Asr (Afternoon)   <code>{asr}</code>\n"
            "🌇 Maghrib (Sunset)  <code>{maghrib}</code>\n"
            "🌙 Isha (Night)      <code>{isha}</code>"
        )
    },
    "btn_refresh": {
        "uz": "🔄 Yangilash",
        "ru": "🔄 Обновить",
        "en": "🔄 Refresh"
    },
    "btn_tomorrow": {
        "uz": "📅 Ertangi kun",
        "ru": "📅 Завтра",
        "en": "📅 Tomorrow"
    },
    "btn_today_inline": {
        "uz": "📅 Bugungi kun",
        "ru": "📅 Сегодня",
        "en": "📅 Today"
    },
    "btn_prev_week": {
        "uz": "◀️ Oldingi hafta",
        "ru": "◀️ Предыдущая неделя",
        "en": "◀️ Previous week"
    },
    "btn_next_week": {
        "uz": "Keyingi hafta ▶️",
        "ru": "Следующая неделя ▶️",
        "en": "Next week ▶️"
    },
    "weekly_template": {
        "uz": (
            "📅 <b>{start_date} – {end_date}</b> — {hudud}\n\n"
            "<code>Sana  | Bomdod | Quyosh | Peshin | Asr   | Shom  | Xufton</code>\n"
            "<code>{rows}</code>"
        ),
        "ru": (
            "📅 <b>{start_date} – {end_date}</b> — {hudud}\n\n"
            "<code>Дата  | Фаджр  | Восход | Зухр   | Аср   | Магриб| Иша</code>\n"
            "<code>{rows}</code>"
        ),
        "en": (
            "📅 <b>{start_date} – {end_date}</b> — {hudud}\n\n"
            "<code>Date  | Fajr   | Sunrise| Dhuhr  | Asr   |Maghrib| Isha</code>\n"
            "<code>{rows}</code>"
        )
    },
    "reminders_menu": {
        "uz": (
            "🔔 <b>Eslatma sozlamalari</b>\n\n"
            "Qaysi namoz vaqtlarida eslatma olishni xohlaysiz? Kerakli tugmani bosing:\n"
            "• Hozirgi bildirishnoma vaqti: <b>{current_before}</b>"
        ),
        "ru": (
            "🔔 <b>Настройки напоминаний</b>\n\n"
            "Для каких намазов вы хотите получать напоминания? Нажмите нужную кнопку:\n"
            "• Текущее время уведомления: <b>{current_before}</b>"
        ),
        "en": (
            "🔔 <b>Reminder Settings</b>\n\n"
            "Which prayers would you like to receive reminders for? Tap to toggle:\n"
            "• Current reminder time: <b>{current_before}</b>"
        )
    },
    "choose_reminder_time": {
        "uz": "⏱ <b>Eslatma namoz vaqtidan necha daqiqa oldin kelsin?</b>",
        "ru": "⏱ <b>За сколько минут до наступления намаза присылать напоминание?</b>",
        "en": "⏱ <b>How many minutes before the prayer should the reminder be sent?</b>"
    },
    "btn_how_many_minutes": {
        "uz": "⏱ Necha daqiqa oldin eslatsin?",
        "ru": "⏱ За сколько минут напоминать?",
        "en": "⏱ How many minutes before?"
    },
    "btn_back": {
        "uz": "⬅️ Orqaga",
        "ru": "⬅️ Назад",
        "en": "⬅️ Back"
    },
    "reminder_options": {
        "uz": {
            0: "Vaqtida",
            10: "10 daqiqa oldin",
            15: "15 daqiqa oldin",
            30: "30 daqiqa oldin"
        },
        "ru": {
            0: "Вовремя",
            10: "За 10 минут",
            15: "За 15 минут",
            30: "За 30 минут"
        },
        "en": {
            0: "On time",
            10: "10 minutes before",
            15: "15 minutes before",
            30: "30 minutes before"
        }
    },
    "ontime_reminder": {
        "uz": (
            "🕌 <b>{namoz_nomi} namozi vaqti kirdi!</b>\n\n"
            "📍 {hudud} — <code>{vaqt}</code>\n\n"
            "{blessing}"
        ),
        "ru": (
            "🕌 <b>Наступило время намаза {namoz_nomi}!</b>\n\n"
            "📍 {hudud} — <code>{vaqt}</code>\n\n"
            "{blessing}"
        ),
        "en": (
            "🕌 <b>It is now time for {namoz_nomi} prayer!</b>\n\n"
            "📍 {hudud} — <code>{vaqt}</code>\n\n"
            "{blessing}"
        )
    },
    "advance_reminder": {
        "uz": (
            "⏳ <b>Eslatma!</b>\n\n"
            "<b>{namoz_nomi}</b> namoziga {daqiqa} daqiqa qoldi (<code>{vaqt}</code>)\n"
            "📍 {hudud}\n\n"
            "{blessing}"
        ),
        "ru": (
            "⏳ <b>Напоминание!</b>\n\n"
            "До намаза <b>{namoz_nomi}</b> осталось {daqiqa} минут (<code>{vaqt}</code>)\n"
            "📍 {hudud}\n\n"
            "{blessing}"
        ),
        "en": (
            "⏳ <b>Reminder!</b>\n\n"
            "<b>{namoz_nomi}</b> prayer is in {daqiqa} minutes (<code>{vaqt}</code>)\n"
            "📍 {hudud}\n\n"
            "{blessing}"
        )
    },
    "settings_menu": {
        "uz": (
            "⚙️ <b>Sozlamalar bo'limi</b>\n\n"
            "📍 Joriy hududingiz: <b>{hudud}</b>\n"
            "🗣 Tanlangan til: <b>{til}</b>\n\n"
            "Nimani o'zgartirmoqchisiz?"
        ),
        "ru": (
            "⚙️ <b>Раздел настроек</b>\n\n"
            "📍 Текущий регион: <b>{hudud}</b>\n"
            "🗣 Выбранный язык: <b>{til}</b>\n\n"
            "Что бы вы хотели изменить?"
        ),
        "en": (
            "⚙️ <b>Settings</b>\n\n"
            "📍 Current region: <b>{hudud}</b>\n"
            "🗣 Selected language: <b>{til}</b>\n\n"
            "What would you like to change?"
        )
    },
    "btn_change_region": {
        "uz": "📍 Hududni o'zgartirish",
        "ru": "📍 Изменить регион",
        "en": "📍 Change region"
    },
    "btn_change_lang": {
        "uz": "🗣 Tilni o'zgartirish",
        "ru": "🗣 Изменить язык",
        "en": "🗣 Change language"
    },
    "btn_manage_reminders": {
        "uz": "🔔 Eslatmalarni boshqarish",
        "ru": "🔔 Управление напоминаниями",
        "en": "🔔 Manage reminders"
    },
    "unknown_cmd": {
        "uz": (
            "Kechirasiz, bu buyruqni to'liq tushunmadim 😊\n\n"
            "Iltimos, qulaylik uchun quyidagi menyu tugmalaridan foydalaning 👇"
        ),
        "ru": (
            "Извините, я не совсем понял вашу команду 😊\n\n"
            "Пожалуйста, воспользуйтесь кнопками меню ниже 👇"
        ),
        "en": (
            "Sorry, I didn't quite catch that command 😊\n\n"
            "Please use the menu buttons below 👇"
        )
    },
    "error_loading": {
        "uz": (
            "Kechirasiz, hozircha bu ma'lumotni topa olmadim, birozdan so'ng qayta urinib ko'ring 🙏"
        ),
        "ru": (
            "Извините, сейчас не удалось загрузить данные, попробуйте чуть позже 🙏"
        ),
        "en": (
            "Sorry, couldn't fetch the data right now, please try again in a moment 🙏"
        )
    }
}


def get_text(key: str, lang: str = "uz", **kwargs) -> str:
    """Xabar matnini tilga moslab formatlab qaytarish."""
    lang_dict = TEXTS.get(key, {})
    raw_text = lang_dict.get(lang) or lang_dict.get("uz") or ""
    if kwargs:
        try:
            return raw_text.format(**kwargs)
        except Exception:
            return raw_text
    return raw_text
