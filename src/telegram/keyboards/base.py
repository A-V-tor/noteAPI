from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.database.models import TelegramUser


async def main_kb(user: TelegramUser):
    keyboard = InlineKeyboardBuilder()

    auth_bt = InlineKeyboardButton(text='Авторизация', callback_data='auth')
    logout_bt = InlineKeyboardButton(text='Выйти', callback_data='logout')
    my_notes_bt = InlineKeyboardButton(
        text='Мои заметки', callback_data=f'my-notes'
    )
    new_note_bt = InlineKeyboardButton(
        text='Новая заметка', callback_data=f'new-note'
    )
    search_note_bt = InlineKeyboardButton(
        text='Поиск', callback_data=f'search-note'
    )

    if not user.token:
        keyboard.row(auth_bt)
    else:
        keyboard.row(my_notes_bt, new_note_bt).row(search_note_bt).row(
            logout_bt
        )

    return keyboard.as_markup()


async def to_main_menu():
    keyboard = InlineKeyboardBuilder()

    to_main_kb = InlineKeyboardButton(text='меню', callback_data='cancel')
    keyboard.row(to_main_kb)

    return keyboard.as_markup()
