import time

import aiohttp
import jwt
from jwt.exceptions import (
    DecodeError,
    ExpiredSignatureError,
    InvalidSignatureError,
)

from config import settings
from src.database.models import TelegramUser


def check_token(token: str):
    try:
        decoded_token = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm_hash]
        )
        return (
            decoded_token if decoded_token['expires'] >= time.time() else None
        )
    except (ExpiredSignatureError, InvalidSignatureError, DecodeError):
        return {}


async def validate_auth_parameters(parameters: str):
    try:
        username, password = parameters.split('-')
        return username, password
    except ValueError:
        return 'Неверный ввод, должен быть в формате username - password: <code>admin - admin</code>'


class ManagerAPI:
    @classmethod
    async def auth(cls, username: str, password: str):
        data = {'username': username, 'password': password}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'http://localhost:8000/api/v1/refresh-jwt', json=data
            ) as resp:
                return await resp.json()

    @classmethod
    async def fetch_all_notes_for_user(cls, telegram_id: int):
        user = await TelegramUser.check_user(telegram_id)
        headers = {'Authorization': f'Bearer {user.token}'}
        async with aiohttp.ClientSession() as session:
            async with session.get(
                'http://localhost:8000/api/v1/notes', headers=headers
            ) as resp:
                return await resp.json()

    @classmethod
    async def create_note(
        cls, telegram_id: int, title: str, text: str, tags: list
    ):
        user = await TelegramUser.check_user(telegram_id)
        headers = {'Authorization': f'Bearer {user.token}'}
        data = {'title': title, 'text': text, 'tags': tags}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'http://localhost:8000/api/v1/note/create',
                headers=headers,
                json=data,
            ) as resp:
                return await resp.json()
