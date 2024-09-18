from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def approve_or_cancel_kb(only_cansel: bool = False):
    keyboard = InlineKeyboardBuilder()

    approve_bt = InlineKeyboardButton(text='Ок', callback_data='approve')
    cancel_kb = InlineKeyboardButton(text='отмена', callback_data='cancel')

    if only_cansel:
        keyboard.row(cancel_kb)
    else:
        keyboard.row(approve_bt, cancel_kb)

    return keyboard.as_markup()
