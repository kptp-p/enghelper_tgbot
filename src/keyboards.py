from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Добавить слово', ), KeyboardButton(text='Удалить слово', )],
        [KeyboardButton(text='Проверить свои знания'), KeyboardButton(text='Список моих слов')],
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите одно из действий',
)


def inline_pagination_keyboard(page, total_page):
    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"page_{page-1}"))
    buttons.append(InlineKeyboardButton(text=f"{page + 1}/{total_page}", callback_data="current_page"))
    if page < total_page - 1:
        buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"page_{page+1}"))
    return InlineKeyboardMarkup(inline_keyboard=[buttons])
