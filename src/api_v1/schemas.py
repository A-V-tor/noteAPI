from datetime import datetime

from pydantic import BaseModel


class UserCreateSchema(BaseModel):
    username: str
    password: str


class UserResponseSchema(BaseModel):
    username: str
    created_at: datetime

    class Config:
        from_attributes = True


class AuthUserSchema(BaseModel):
    username: str
    password: str


class AllNotesSchema(BaseModel):
    id: int
    user_id: int
    title: str
    text: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NewNoteSchema(BaseModel):
    title: str
    text: str
    tags: list[str] | list


class EditNoteBody(BaseModel):
    text: str