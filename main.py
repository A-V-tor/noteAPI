import uvicorn
from fastapi import FastAPI
from src.api_v1.routes import router


def create_web_app():
    app = FastAPI(docs_url='/docs')
    app.include_router(router)

    return app


if __name__ == '__main__':
    uvicorn.run(f'{__name__}:create_web_app', host='0.0.0.0', reload=True)
