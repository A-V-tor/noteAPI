from fastapi import APIRouter


router = APIRouter()


@router.get("/test")
async def handler():
    return {"status": "OK"}