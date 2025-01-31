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


async def count_words(tg_id: int):
    '''Возвращает количество слов пользователя'''
    async with async_session() as session:
        return await session.scalar(select(func.count(Word.id)).where(Word.user_id == tg_id))


async def get_my_words(tg_id: int, offset: int = 0):
    '''Возвращает список слов пользователя с пагинацией'''
    async with async_session() as session:
        if await session.scalar(select(func.count(Word.id)).where(Word.user_id == tg_id)) != 0:
            return await session.scalars(
                select(Word)
                .where(Word.user_id == tg_id)
                .offset(offset)
                .limit(DEFAULT_LIMIT_WORDLIST)
            )
        else:
            return
