from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Тренировка", callback_data="training")],
        [InlineKeyboardButton(text="Контрольный кейс", callback_data="training")]
    ])

def training_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Сахарный диабет", callback_data="disease:diabetes")],
        [InlineKeyboardButton(text="Анемия", callback_data="disease:anemia")],
        [InlineKeyboardButton(text="Туберкулез", callback_data="disease:tuberculosis")],
        [InlineKeyboardButton(text="Аппендицит", callback_data="disease:appendicitis")],
        [InlineKeyboardButton(text="Эпилепсия", callback_data="disease:epilepsy")]
    ])

