import time
from datetime import datetime

import jwt
from passlib.context import CryptContext
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    and_,
    delete,
    desc,
    func,
    select,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

from config import settings, LOGGER
from src.database.base import Base, async_session_factory

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


notes_tags_table = Table(
    'notes_tags_table_association',
    Base.metadata,
    Column(
        'notes_id',
        Integer,
        ForeignKey('notes.id'),
        primary_key=True,
    ),
    Column('tags_id', Integer, ForeignKey('tags.id'), primary_key=True),
)


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    token: Mapped[str] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )

    notes: Mapped['Note'] = relationship('Note', back_populates='user')

    @classmethod
    async def add_user(cls, username: str, password: str):
        hash_password = pwd_context.hash(password)

        async with async_session_factory() as session:
            new_user = cls(
                username=username,
                password=hash_password,
            )
            session.add(new_user)
            await session.flush()

            token = await cls.__generate_jwt_token(new_user.id)
            new_user.token = token

            try:
                await session.commit()
                return new_user
            except IntegrityError as e:
                LOGGER.exception(e)
                await session.rollback()
                return None

    @classmethod
    async def get_user(cls, username: str, password: str):
        async with async_session_factory() as session:
            user = await session.scalar(
                select(cls).where(and_(cls.username == username))
            )
            check_password = pwd_context.verify(password, user.password)

            if user and check_password:
                return user

    @classmethod
    async def new_jwt_token(cls, username: str, password: str):
        async with async_session_factory() as session:
            user = await session.scalar(
                select(cls).where(and_(cls.username == username))
            )
            check_password = pwd_context.verify(password, user.password)

            if user and check_password:
                token = await cls.__generate_jwt_token(user.id)
                user.token = token
                await session.commit()

                return token

    @staticmethod
    async def __generate_jwt_token(username: str):
        payload = {'user_id': username, 'expires': time.time() + 86400}
        token = jwt.encode(
            payload, settings.secret_key, algorithm=settings.algorithm_hash
        )

        return token


class Note(Base):
    __tablename__ = 'notes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[[str]] = mapped_column(String(255), nullable=False)
    text: Mapped[[str]] = mapped_column(Text(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )
    tags = relationship(
        'Tag',
        secondary=notes_tags_table,
        back_populates='notes',
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'), nullable=False
    )
    user: Mapped['User'] = relationship('User', back_populates='notes')

    @classmethod
    async def get_all_notes(cls, user_id: int):
        async with async_session_factory() as session:
            notes = (
                (
                    await session.execute(
                        select(cls)
                        .where(cls.user_id.in_([user_id]))
                        .options(selectinload(cls.tags))
                        .order_by(desc(cls.created_at))
                    )
                )
                .scalars()
                .all()
            )
            return notes

    @classmethod
    async def create_note(
        cls, user_id: int, title: str, text: str, tags: list['Tag']
    ):
        async with async_session_factory() as session:
            note = cls(title=title, text=text, user_id=user_id, tags=tags)
            session.add(note)
            try:
                await session.commit()
                return note
            except IntegrityError as e:
                LOGGER.exception(e)
                await session.rollback()
                return None

    @classmethod
    async def get_note(cls, id_: int):
        async with async_session_factory() as session:
            note = await session.scalar(
                select(cls)
                .where(cls.id.in_([id_]))
                .options(selectinload(cls.tags))
            )
            return note

    @classmethod
    async def delete_note(cls, id_: int):
        async with async_session_factory() as session:
            await session.execute(delete(cls).where(cls.id.in_([id_])))
            await session.commit()

    @classmethod
    async def edit_note(cls, id_: int, text: str):
        async with async_session_factory() as session:
            note = await cls.get_note(id_)
            note.text = text

            session.add(note)
            await session.commit()

    @classmethod
    async def edit_tags_note(cls, id_: int, tags: list):
        async with async_session_factory() as session:
            note = await cls.get_note(id_)
            tags = await Tag.get_tags_by_title(tags)
            note.tags = tags

            session.add(note)
            await session.commit()


class Tag(Base):
    __tablename__ = 'tags'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[[str]] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )
    notes = relationship(
        'Note',
        secondary=notes_tags_table,
        back_populates='tags',
    )

    @classmethod
    async def get_tags_by_title(cls, title_list: list):
        async with async_session_factory() as session:
            tags = (
                (
                    await session.execute(
                        select(cls).where(cls.title.in_(title_list))
                    )
                )
                .scalars()
                .all()
            )
            if not tags or len(tags) != len(title_list):
                tags = await cls.create_tags(title_list)

            return tags

    @classmethod
    async def create_tag(cls, title: str):
        async with async_session_factory() as session:
            tag = cls(title=title)
            session.add(tag)
            await session.commit()
            return tag

    @classmethod
    async def create_tags(cls, title_list: list):
        list_tags = []
        async with async_session_factory() as session:
            for title in title_list:
                tag = cls(title=title)
                session.add(tag)
                await session.flush()
                list_tags.append(tag)
            await session.commit()

        return list_tags


class TelegramUser(Base):
    __tablename__ = 'telegram_users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False
    )
    token: Mapped[str] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )

    @classmethod
    async def create_user(cls, telegram_id: int):
        async with async_session_factory() as session:
            new_user = cls(telegram_id=telegram_id)
            session.add(new_user)
            try:
                await session.commit()
                return new_user
            except IntegrityError as e:
                LOGGER.exception(e)
                await session.rollback()
                return None

    @classmethod
    async def check_user(cls, telegram_id: int):
        async with async_session_factory() as session:
            user = await session.scalar(
                select(cls).where(cls.telegram_id.in_([telegram_id]))
            )

            return user

    @classmethod
    async def new_jwt_token(cls, telegram_id: int, token: str):
        async with async_session_factory() as session:
            user = await session.scalar(
                select(cls).where(cls.telegram_id == telegram_id)
            )

            if user:
                user.token = token
                await session.commit()

                return token

    @classmethod
    async def delete_token(cls, telegram_id: int):
        async with async_session_factory() as session:
            user = await session.scalar(
                select(cls).where(cls.telegram_id == telegram_id)
            )

            if user:
                user.token = None
                await session.commit()

                return True
