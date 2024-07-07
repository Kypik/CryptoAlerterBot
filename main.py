import asyncio
import logging

from config_reader import config
from db import creat_table
import handlers
import utils

from aiogram import Bot, Dispatcher

async def main():
    logging.basicConfig(level=logging.INFO)

    await creat_table()
    
    bot = Bot(token = config.bot_token.get_secret_value())
    dp = Dispatcher()
    
    dp.include_router(handlers.router)

    check_task = asyncio.create_task(utils.start_check(bot))
    polling_task = asyncio.create_task(dp.start_polling(bot))

    # Запускаем обе задачи параллельно
    await asyncio.gather(check_task, polling_task)

if __name__ == "__main__":
    asyncio.run(main())
        