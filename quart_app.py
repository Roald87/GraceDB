import asyncio
import logging

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook

from config import API_TOKEN, get_host, get_port, get_secret, get_webhook_url

# webhook settings
WEBHOOK_URL = get_webhook_url()

# webserver settings
WEBAPP_HOST = get_host()
WEBAPP_PORT = get_port()

logging.basicConfig(level=logging.INFO)

loop = asyncio.get_event_loop()
bot = Bot(token=API_TOKEN, loop=loop)
dp = Dispatcher(bot)


@dp.message_handler()
async def echo(message: types.Message):
    await bot.send_message(message.chat.id, message.text)


async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)
    # insert code here to run it after start


async def on_shutdown(dp):
    # insert code here to run it before shutdown
    pass


if __name__ == '__main__':
    start_webhook(
        dispatcher=dp, webhook_path=f'/{get_secret()}',
        on_startup=on_startup, on_shutdown=on_shutdown,
        skip_updates=True, host=WEBAPP_HOST, port=WEBAPP_PORT
    )