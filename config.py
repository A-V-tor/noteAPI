import os

from dotenv import load_dotenv

load_dotenv()


class DatabaseConfig:
    db_host: str = os.getenv("DB_HOST")
    db_port: str = os.getenv("DB_PORT")
    db_name: str = os.getenv("DB_NAME")
    db_user: str = os.getenv("DB_USER")
    db_pass: str = os.getenv("DB_PASS")

    db_url = f"postgresql+asyncpg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"


class Config:
    db_url: str = DatabaseConfig.db_url
    secret_key: str = os.getenv("SECRET_KEY")
    algorithm_hash: str = os.getenv("ALGORITHM_HASH")


settings = Config()