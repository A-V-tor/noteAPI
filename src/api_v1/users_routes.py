from fastapi import APIRouter, HTTPException, status

from src.api_v1.schemas import (
    AuthUserSchema,
    UserCreateSchema,
    UserResponseSchema,
)
from src.database.models import User

router = APIRouter(prefix='/api/v1')


@router.post('/user/create', response_model=UserResponseSchema, tags=['user'])
async def create_user(user: UserCreateSchema):
    user = await User.add_user(user.username, user.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Username already registered',
        )

    return UserResponseSchema.model_validate(user)


@router.post('/refresh-jwt', tags=['user'])
async def login(user: AuthUserSchema):
    token = await User.new_jwt_token(user.username, user.password)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User not found'
        )

    return {'token': f'Bearer {token}'}
