from sqlalchemy import select, func, delete, update
from string import ascii_lowercase

from .models import LastWordUser, async_session
from .models import User, Word

DEFAULT_LIMIT_WORDLIST = 10


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
        return None


async def check_last_word_and_get(tg_id: int):
    '''Проверяет последнее слово пользователя'''
    async with async_session() as session:
        last_word = await session.scalar(
                select(LastWordUser).where(LastWordUser.user_id == tg_id)
            )
        if not last_word:
            word = await get_random_word(tg_id)
            session.add(LastWordUser(user_id=tg_id, word_id=word.id))
            await session.commit()
            return word

        word_count = await session.scalar(
            select(func.count()).where(Word.user_id == tg_id)
        )
        if word_count > 1:
            while True:
                word = await get_random_word(tg_id)
                if word.id != last_word.word_id:
                    await session.execute(update(LastWordUser).where(LastWordUser.user_id == tg_id).values(word_id=word.id))
                    await session.commit()
                    return word
        return await get_random_word(tg_id)


async def check_is_latin(input_word: str):
    '''Проверяет все ли символы слова являются латинскими буквами'''
    return all(char in ascii_lowercase for char in input_word)


async def get_my_words(tg_id: int, offset: int):
    '''Возвращает список слов пользователя с пагинацией'''
    async with async_session() as session:
        if await session.scalar(select(func.count(Word.id)).where(Word.user_id == tg_id)) != 0:
            return await session.scalars(
                select(Word)
                .where(Word.user_id == tg_id)
                .offset(offset)
                .limit(DEFAULT_LIMIT_WORDLIST)
            )
        return


async def count_words(tg_id: int):
    '''Возвращает количество слов пользователя'''
    async with async_session() as session:
        return await session.scalar(select(func.count(Word.id)).where(Word.user_id == tg_id))


async def delete_word(tg_id: int, word: str) -> bool:
    async with async_session() as session:
        result = await session.execute(delete(Word).where(Word.user_id == tg_id, Word.word == word).returning(Word.id))
        await session.commit()
        return result is not None
