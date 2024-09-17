import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher

from config import Config
from src.telegram.handlers.base import router as base_router
from src.telegram.handlers.notes import router as notes_router

token = Config.bot_token


async def main():
    bot = Bot(token)

    dp = Dispatcher()
    dp.include_routers(base_router)
    dp.include_routers(notes_router)

    await dp.start_polling(
        bot,
        skip_updates=True,
    )


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format='%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s',
        datefmt='%Y-%m-%d,%H:%M:%S',
    )
    asyncio.run(main())
