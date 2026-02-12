from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup,BotCommand
from aiogram.utils.keyboard import ReplyKeyboardBuilder

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
def get_main_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="🏥 Тренажер")
    builder.button(text="ℹ️ Помощь")
    builder.adjust(1)
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False
    )

async def set_bot_commands(bot):
    commands = [
        BotCommand(command="start", description="🏥 Главное меню"),
        BotCommand(command="help", description="📖 Помощь и инструкции"),
        BotCommand(command="завершить", description="⏹️ Завершить диалог"),
        BotCommand(command="диагноз", description="🩺 Поставить диагноз")
    ]
    await bot.set_my_commands(commands)