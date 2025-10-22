import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from db import init_db, export_to_excel_loop
from handlers.handlers import router
async def main():
    init_db()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    # Запускаем фоновую задачу (параллельно с ботом)
    asyncio.create_task(export_to_excel_loop())

    print("🤖 Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
