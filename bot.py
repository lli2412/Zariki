from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from .settings import BOT_TOKEN

_session = AiohttpSession()
bot = Bot(token=BOT_TOKEN, session=_session)
