from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.filters.command import CommandStart
from aiogram.fsm.context import FSMContext

from src.database.models import TelegramUser
from src.telegram.keyboards.base import main_kb

router = Router(name='base')


@router.callback_query(StateFilter('*'), F.data == 'cancel')
async def cancel_callback(callback: types.CallbackQuery, state: FSMContext):
    """Сброс всех конечных автоматов/отмена всех состояний."""
    await state.clear()
    tg_id = callback.from_user.id
    user = await TelegramUser.check_user(tg_id)

    await callback.message.answer(f'МЕНЮ', reply_markup=await main_kb(user))


@router.message(CommandStart())
async def start_handler(message: types.Message):
    """Получение стартового меню и клавиатуры."""
    tg_id = message.from_user.id
    user = await TelegramUser.check_user(tg_id)

    if not user:
        user = await TelegramUser.create_user(tg_id)

    await message.answer(f'МЕНЮ', reply_markup=await main_kb(user))
