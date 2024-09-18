from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.util import await_fallback

from config import LOGGER
from src.database.models import TelegramUser
from src.telegram.keyboards.base import main_kb, to_main_menu
from src.telegram.keyboards.notes import approve_or_cancel_kb
from src.telegram.states import AuthDataState, NewNoteState, SearchNoteState
from src.tools import ManagerAPI, validate_auth_parameters

router = Router(name='notes')
manager_api = ManagerAPI()


@router.callback_query(F.data == 'auth')
async def start_auth(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        'Введите юзернейм и пароль в формате: username - password.Например: admin - admin'
    )

    await state.set_state(AuthDataState.auth)


@router.message(AuthDataState.auth)
async def request_to_api(message: types.Message, state: FSMContext):
    check = await validate_auth_parameters(message.text)
    if len(check) < 2:
        await message.answer(check, parse_mode='HTML')
        return
    res = await manager_api.auth(check[0], check[1])

    msg = 'Неудачная попытка авторизации, попробуйте немного позже'
    await state.clear()

    if 'token' in res:
        tg_id = message.from_user.id
        auth_token = res['token'].split(' ')[-1]
        await TelegramUser.new_jwt_token(tg_id, auth_token)
        msg = 'Вы авторизованы'
    await message.answer(
        msg, parse_mode='HTML', reply_markup=await to_main_menu()
    )


@router.callback_query(F.data == 'logout')
async def logout(callback: types.CallbackQuery):
    msg = 'Что-то пошло не так...'
    tg_id = callback.from_user.id
    user = await TelegramUser.check_user(tg_id)
    check_delete = await TelegramUser.delete_token(tg_id)

    if check_delete:
        msg = 'Вы разлогинились в сервисе заметок'
    await callback.message.answer(msg, reply_markup=await main_kb(user))


@router.callback_query(F.data == 'my-notes')
async def all_notes(callback: types.CallbackQuery):
    msg = 'У вас нет заметок'

    tg_id = callback.from_user.id
    notes = await manager_api.fetch_all_notes_for_user(tg_id)
    if notes:
        note_msg = ''
        for note in notes:
            tags = [tag['title'] for tag in note['tags'] if tag]
            note_msg += f'Название: <b>{note["title"]}</b>\n'
            note_msg += f'теги: ❗️{tags} ❗️\n'
            note_msg += f'<i>{note["created_at"]}</i>\n'
            note_msg += f'{note["text"]}\n\n'

        msg = note_msg

    for x in range(0, len(msg), 4096):
        await callback.message.answer(
            msg[x : x + 4096],
            parse_mode='HTML',
            reply_markup=await to_main_menu(),
        )


@router.callback_query(F.data == 'new-note')
async def new_note_start_state(
    callback: types.CallbackQuery, state: FSMContext
):
    msg = 'Введите текст вашей заметки'
    await state.set_state(NewNoteState.add_text)

    await callback.message.answer(
        msg, reply_markup=await approve_or_cancel_kb(True)
    )


@router.message(NewNoteState.add_text)
async def text_for_note(message: types.Message, state: FSMContext):
    msg = 'Добавьте название заметки'
    text = message.text
    await state.set_data({'text': text})

    await state.set_state(NewNoteState.add_title)
    await message.answer(msg, reply_markup=await approve_or_cancel_kb(True))


@router.message(NewNoteState.add_title)
async def title_for_note(message: types.Message, state: FSMContext):
    msg = 'Добавьте названия тегов для заметки через запятую, например: траты, деньги'
    title = message.text
    data = await state.get_data()
    data.update({'title': title})
    await state.set_data(data)

    await state.set_state(NewNoteState.add_tags)
    await message.answer(msg, reply_markup=await approve_or_cancel_kb(True))


@router.message(NewNoteState.add_tags)
async def tags_for_note(message: types.Message, state: FSMContext):
    data = await state.get_data()
    text = message.text

    try:
        tags = text.split(',')
        data.update({'tags': tags})
        await state.set_data(data)
    except ValueError:
        LOGGER.exception(f'Передан неверный формат записи: {text}')
        await message.answer('Передан неверный формат записи')
        return

    await message.answer(
        'Добавляем заметку?', reply_markup=await approve_or_cancel_kb()
    )


@router.callback_query(F.data == 'approve')
async def add_note(callback: types.CallbackQuery, state: FSMContext):
    tg_id = callback.from_user.id
    user = await TelegramUser.check_user(tg_id)
    msg = 'Что-то пошло не так...'
    data = await state.get_data()

    title = data['title']
    text = data['text']
    tags = data['tags']
    res = await manager_api.create_note(tg_id, title, text, tags)

    if res.get('status'):
        msg = 'Заметка добавлена'

    await callback.message.answer(msg, reply_markup=await main_kb(user))


@router.callback_query(F.data == 'search-note')
async def search_note_start_state(
    callback: types.CallbackQuery, state: FSMContext
):
    msg = 'Введите через запятую интересующие вас теги, например: тренировки, покупки'

    await state.set_state(SearchNoteState.tags)
    await callback.message.answer(
        msg, reply_markup=await approve_or_cancel_kb(True)
    )


@router.message(SearchNoteState.tags)
async def tags_for_search(message: types.Message):
    msg = 'Что-то пошло не так...'
    try:
        search_tags = message.text.split(',')
    except ValueError:
        LOGGER.exception(f'Неверный формат ввода {message.text}')
        await message.answer(
            'Неверный формат ввода!',
            reply_markup=await approve_or_cancel_kb(True),
        )
        return
    tg_id = message.from_user.id
    notes = await manager_api.fetch_all_notes_for_user(tg_id)

    if notes:
        note_msg = ''
        for note in notes:
            tags = [tag['title'] for tag in note['tags'] if tag]
            intersection = set(search_tags) & set(tags)

            if not intersection:
                continue

            note_msg += f'Название: <b>{note["title"]}</b>\n'
            note_msg += f'теги: ❗️{tags} ❗️\n'
            note_msg += f'<i>{note["created_at"]}</i>\n'
            note_msg += f'{note["text"]}\n\n'

        msg = note_msg

    for x in range(0, len(msg), 4096):
        await message.answer(
            msg[x : x + 4096],
            parse_mode='HTML',
            reply_markup=await to_main_menu(),
        )
