from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Добавить слово', ),],
        [KeyboardButton(text='Проверить свои знания'), KeyboardButton(text='Список моих слов')],
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите одно из действий',
)

