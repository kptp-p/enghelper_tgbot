from sqlalchemy import select, func
from string import ascii_lowercase

from .models import async_session
from .models import User, Word

DEFAULT_LIMIT_WORDLIST = 100

async def set_user(tg_id: int):
    '''Добавляет пользователя в базу данных'''
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()


async def add_word_translate(tg_id: int, word: str, translate: str):
    '''Проверяет существует ли слово в словаре и добавляет его в словарь'''
    async with async_session() as session:
        if await session.scalar(select(Word).where(Word.word==word, Word.user_id==tg_id)):
            return True
        else:
            session.add(Word(word=word, translate=translate, user_id=tg_id))
            await session.commit()


async def get_random_word(tg_id: int):
    '''Возвращает случайное слово из словаря'''
    async with async_session() as session:

        word = await session.scalar(
            select(Word).where(Word.user_id == tg_id).order_by(func.random()).limit(1)
        )
        if word:
            return word
        else:
            return None


async def check_is_latin(input_word: str):
    '''Проверяет все ли символы слова являются латинскими буквами'''
    return all(char in ascii_lowercase for char in input_word)


