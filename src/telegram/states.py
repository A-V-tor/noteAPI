from aiogram.fsm.state import State, StatesGroup


class AuthDataState(StatesGroup):
    auth = State()


class NewNoteState(StatesGroup):
    add_text = State()
    add_title = State()
    add_tags = State()


class SearchNoteState(StatesGroup):
    tags = State()
