import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from src.models import async_main
from src.handlers import router


load_dotenv()


dp = Dispatcher()


async def main():
    bot = Bot(token=os.getenv('BOT_TOKEN'))
    await async_main()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bye!")
