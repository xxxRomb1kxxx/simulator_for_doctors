from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Тренировка", callback_data="training")],
        [InlineKeyboardButton(text="Контрольный кейс", callback_data="control_case")]
    ])

def training_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Сахарный диабет", callback_data="disease:diabetes")],
        [InlineKeyboardButton(text="Анемия", callback_data="disease:anemia")],
        [InlineKeyboardButton(text="Туберкулез", callback_data="disease:tuberculosis")],
        [InlineKeyboardButton(text="Аппендицит", callback_data="disease:appendicitis")],
        [InlineKeyboardButton(text="Эпилепсия", callback_data="disease:epilepsy")]
    ])
def dialog_control_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏥 Поставить диагноз", callback_data="cmd:diagnosis")],
        [InlineKeyboardButton(text="✅ Завершить", callback_data="cmd:finish")]
    ])
