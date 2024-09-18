import os
from contextlib import asynccontextmanager

import redis.asyncio as redis
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter

from src.api_v1.notes_routes import router as users_notes
from src.api_v1.users_routes import router as users_routes

load_dotenv()
redis_url = os.getenv('REDIS_URL')


@asynccontextmanager
async def lifespan(_: FastAPI):
    redis_connection = redis.from_url(f'redis://{redis_url}', encoding='utf8')
    await FastAPILimiter.init(redis_connection)
    yield
    await FastAPILimiter.close()


def create_web_app():
    app = FastAPI(lifespan=lifespan, docs_url='/docs')
    app.include_router(users_routes)
    app.include_router(users_notes)

    return app


if __name__ == '__main__':
    uvicorn.run(f'{__name__}:create_web_app', host='0.0.0.0', reload=True)
