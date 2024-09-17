import uvicorn
from fastapi import FastAPI
from src.api_v1.users_routes import router as users_routes
from src.api_v1.notes_routes import router as users_notes


def create_web_app():
    app = FastAPI(docs_url='/docs')
    app.include_router(users_routes)
    app.include_router(users_notes)

    return app


if __name__ == '__main__':
    uvicorn.run(f'{__name__}:create_web_app', host='0.0.0.0', reload=True)
