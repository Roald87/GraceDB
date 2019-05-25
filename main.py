import logging

from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook

from config import API_TOKEN, secret
from gracebot import GraceBot
from ngrok import get_ngrok_url, get_port

# webhook settings
WEBHOOK_URL = f'{get_ngrok_url()}/{secret}'

# webserver settings
WEBAPP_HOST = 'localhost'
WEBAPP_PORT = get_port()

logging.basicConfig(level=logging.INFO)

async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)


async def on_shutdown(dp):
    # insert code here to run it before shutdown
    pass


bot = GraceBot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def echo(message: types.Message):
    await bot.send_message(message.chat.id, bot.welcome_message)


@dp.message_handler(commands=['latest'])
async def echo(message: types.Message):
    await bot.send_message(message.chat.id, bot.latest_message, parse_mode='markdown')

    with open(bot.latest_image(), 'rb') as picture:
        await bot.send_photo(message.chat.id, picture)


if __name__ == '__main__':
    start_webhook(
        dispatcher=dp, webhook_path=f'/{secret}',
        on_startup=on_startup, on_shutdown=on_shutdown,
        skip_updates=True, host=WEBAPP_HOST, port=WEBAPP_PORT
    )