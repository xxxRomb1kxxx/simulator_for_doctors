from aiogram.fsm.state import StatesGroup, State

class DialogState(StatesGroup):
    waiting_question = State()
    waiting_diagnosis = State()
