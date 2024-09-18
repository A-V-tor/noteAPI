import os

from datetime import datetime
from dotenv import load_dotenv
from loguru import logger


load_dotenv()


class DatabaseConfig:
    db_host: str = os.getenv('DB_HOST')
    db_port: str = os.getenv('DB_PORT')
    db_name: str = os.getenv('DB_NAME')
    db_user: str = os.getenv('DB_USER')
    db_pass: str = os.getenv('DB_PASS')

    db_url = f'postgresql+asyncpg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'


class Config:
    db_url: str = DatabaseConfig.db_url
    secret_key: str = os.getenv('SECRET_KEY')
    algorithm_hash: str = os.getenv('ALGORITHM_HASH')
    bot_token: str = os.getenv('BOT_TOKEN')


class LoggerConfig:
    logger = logger

    def __init__(self) -> None:
        current_date = datetime.now().strftime('%Y-%m-%d')
        log_file = f'logs/{current_date}.log'

        self.logger.add(
            log_file,
            backtrace=True,
            diagnose=True,
            rotation='00:00',
            retention='10 days'
        )


settings = Config()
LOGGER = LoggerConfig().logger
