"""
FSM (Finite State Machine) holatlari
"""

from aiogram.fsm.state import State, StatesGroup

class ApplicationForm(StatesGroup):
    """Ariza topshirish bosqichlari"""
    vacancy = State()
    fullname = State()
    phone = State()
    experience = State()
    salary = State()
    portfolio = State()
    resume = State()
    confirm = State()

class QuickCVForm(StatesGroup):
    """Tezkor rezyume tahlili holati"""
    waiting_for_cv = State()

class AdminCustomMessageForm(StatesGroup):
    """HR tomonidan nomzodga xabar yuborish holati"""
    waiting_for_message = State()
