import asyncio
from aiogram import Bot, Dispatcher
from config import TOKEN
from handlers.users import load_banned_words
from handlers import users
from database import create_pool

async def main():
    bot = Bot(token=TOKEN)  
    dp = Dispatcher()

    db_pool = await create_pool()
    dp['db_pool'] = db_pool
    dp.include_router(users.router)

    await load_banned_words(db_pool)

    print("я запущен и готов к работе!")

    try:  
       await dp.start_polling(bot)
    finally:
        await db_pool.close()


if __name__ == "__main__":
    asyncio.run(main()) 