import math
from aiogram.filters.command import Command
from aiogram import Router, types, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext


from src import requests as rq
from src import keyboards as kb

router = Router()


class AddWord(StatesGroup):
    word = State()
    translate = State()


class DeleteWord(StatesGroup):
    word = State()


class CheckMyKnowledge(StatesGroup):
    count_words = State()
    waiting_translate_word = State()


@router.message(Command('start'))
async def cmd_start(message: types.Message):
    try:
        await rq.set_user(message.from_user.id) 
        await message.answer('Привет, я твой личный словарь английских слов. Ты можешь добавить слово в словарь, а потом проверить свои знания!', reply_markup=kb.main)
    except Exception as e:
        return e


@router.message(Command('help'))
async def cmd_help(message: types.Message):
    await message.answer('Чтобы добавить слово в словарь, напиши /add. Чтобы проверить свои знания, напиши /check')


@router.message(F.text == 'Добавить слово')
async def cmd_add_word_first(message: types.Message, state: FSMContext):
    try:
        await state.set_state(AddWord.word)
        await message.answer('Впишите слово на английском, которое хотите добавить')
    except Exception as e:
        return e


@router.message(AddWord.word)
async def cmd_add_word_second(message: types.Message, state: FSMContext):
    try:
        if await rq.check_is_latin(message.text.lower()):
            await state.update_data(word=message.text.lower())
            await state.set_state(AddWord.translate)
            await message.answer('Впишите перевод слова')
        else:
            await message.answer('Слово должно состоять только из латинских букв')
            await state.clear()
    except Exception as e:
        await state.clear()
        return e


@router.message(AddWord.translate)
async def cmd_add_word_third(message: types.Message, state: FSMContext):
    try:
        await state.update_data(translate=message.text.lower())
        data = await state.get_data()
        if await rq.add_word_translate(message.from_user.id, data['word'], data['translate']):
            await message.answer(f'Слово {data["word"]} уже есть в словаре')
        else:
            await message.answer(f'Слово {data["word"]} успешно добавлено в словарь')
    except Exception as e:
        await message.answer(f'Произошла ошибка: {e}')
    finally:
        await state.clear()


@router.message(F.text == 'Проверить свои знания')
async def cmd_check_my_knowledge(message: types.Message, state: FSMContext):
    try:
        await state.clear()
        word = await rq.check_last_word_and_get(message.from_user.id)
        if word:
            await state.update_data(word=word.word, translate=word.translate)
            await state.set_state(CheckMyKnowledge.waiting_translate_word)
            await message.answer(f'Переведите слово: {word.word}')
        else:
            await message.answer('У вас нет слов в словаре')
    except Exception as e:
        await message.answer(f'Произошла ошибка: {e}')


@router.message(CheckMyKnowledge.waiting_translate_word)
async def cmd_check_my_knowledge_second(message: types.Message, state: FSMContext):
    try:
        await state.update_data(waiting_translate_word=message.text.lower())
        data = await state.get_data()
        if data['translate'] != data['waiting_translate_word']:
            await message.answer(f'К сожалению, вы ошиблись. Правильный перевод слова {data["word"]} будет {data["translate"]}')
        else:
            await message.answer('Вы перевели правильно')
    except Exception as e:
        await message.answer(f'Произошла ошибка: {e}')
    finally:
        await state.clear()


@router.message(F.text == 'Список моих слов')
async def cmd_get_my_words(message: types.Message, state: FSMContext):
    try:
        page = 0
        total_count_words = await rq.count_words(message.from_user.id)
        total_page = math.ceil(total_count_words / rq.DEFAULT_LIMIT_WORDLIST)
        words = await rq.get_my_words(message.from_user.id, page * rq.DEFAULT_LIMIT_WORDLIST)

        if words:
            words_list = [word.word + ' - ' + word.translate for word in words]
            await message.answer('\n'.join(words_list), reply_markup=kb.inline_pagination_keyboard(page, total_page))
        else:
            await message.answer('У вас нет слов в словаре')
    except Exception as e:
        await e


@router.callback_query(F.data.startswith('page_'))
async def pagination_callback(callback_query: types.CallbackQuery):
    try:
        page = int(callback_query.data.split('_')[1])
        total_count_words = await rq.count_words(callback_query.from_user.id)
        total_page = math.ceil(total_count_words / rq.DEFAULT_LIMIT_WORDLIST)
        words = await rq.get_my_words(callback_query.from_user.id, page * rq.DEFAULT_LIMIT_WORDLIST)
        if words:
            words_list = [word.word + ' - ' + word.translate for word in words]
            keyboard = kb.inline_pagination_keyboard(page, total_page)
            await callback_query.message.edit_text('\n'.join(words_list), reply_markup=keyboard)
            await callback_query.answer()
        else:
            await callback_query.answer('У вас нет слов в словаре, для начала добавьте их')
    except Exception as e:
        return e


@router.message(F.text == 'Удалить слово')
async def cmd_delete_word(message: types.Message, state: FSMContext):
    await message.answer('Впишите слово, которое хотите удалить')
    await state.set_state(DeleteWord.word)


@router.message(DeleteWord.word)
async def cmd_delete_word_second(message: types.Message, state: FSMContext):
    try:
        await state.update_data(word=message.text.lower())
        if await rq.delete_word(message.from_user.id, message.text.lower()):
            await message.answer(f'Слово {message.text.lower()} успешно удалено')
        else:
            await message.answer(f'Слово {message.text.lower()} не найдено в словаре')
    except Exception as e:
        return e
