import asyncio
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from .bot import bot
from . import handlers
from .db import init_db
from .settings import DATABASE_URL, BOT_TOKEN

async def main():
    await init_db(DATABASE_URL)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    # register handlers
    dp.message.register(handlers.cmd_start, commands=["start"])
    dp.message.register(handlers.cmd_balance, commands=["balance"])
    dp.message.register(handlers.cmd_create, commands=["create"])
    dp.message.register(handlers.cmd_open, commands=["open"])
    # join needs dp.storage passed when calling handler from message
    async def cmd_join_wrapper(m):
        return await handlers.cmd_join(m, dp.storage)
    dp.message.register(cmd_join_wrapper, commands=["join"])
    dp.callback_query.register(handlers.cb_amount, F.data.startswith("amount:"))
    dp.message.register(handlers.msg_custom_amount, handlers.CreateStates.choosing_amount)
    dp.callback_query.register(handlers.cb_pick_create, F.data.startswith("pick:"), state=handlers.CreateStates.choosing_pick)
    dp.callback_query.register(handlers.cb_pick_join, F.data.startswith("pick:"))  # for join (will check storage)
    dp.callback_query.register(handlers.cb_cancel, F.data=="confirm:cancel", state=handlers.CreateStates.confirming)
    dp.callback_query.register(handlers.cb_confirm_create, F.data=="confirm:create", state=handlers.CreateStates.confirming)

    print("Bot started (press Ctrl+C to stop)")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
