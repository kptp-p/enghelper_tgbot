from random import randint
from sqlalchemy import select, func

from .models import async_session
from .models import User, Word


async def set_user(tg_id):
    '''Добавляет пользователя в базу данных'''
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()


async def add_word_translate(tg_id, word, translate):
    '''Добавляет слово в словарь'''
    async with async_session() as session:
        if await session.scalar(select(Word).where(Word.word==word, Word.user_id==tg_id)):
            return True
        else:
            session.add(Word(word=word, translate=translate, user_id=tg_id))
            await session.commit()


async def get_random_word(tg_id):
    '''Возвращает случайное слово из словаря'''
    async with async_session() as session:

        try:
            word = await session.scalar(
                select(Word).where(Word.user_id == tg_id).order_by(func.random()).limit(1)
            )
            if word:
                return word
            else:
                return None
        except Exception as e:
            return e
