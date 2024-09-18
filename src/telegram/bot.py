import asyncio

from aiogram import Bot, Dispatcher

from config import LOGGER, settings
from src.telegram.handlers.base import router as base_router
from src.telegram.handlers.notes import router as notes_router

token = settings.bot_token


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
    LOGGER.info('Бот запущен')
    asyncio.run(main())
    LOGGER.info('Бот остановлен')
