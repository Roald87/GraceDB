import logging

from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook

from config import API_TOKEN, secret
from gracebot import GraceBot
from ngrok import get_ngrok_url, get_port

logging.basicConfig(level=logging.INFO)

bot = GraceBot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def echo(message: types.Message):
    await bot.send_welcome_message(message)


@dp.message_handler(commands=['latest'])
async def echo(message: types.Message):
    await bot.send_latest(message)

@dp.message_handler(commands=['stats'])
async def echo(message: types.Message):
    await bot.send_o3_stats(message)


async def on_startup(dp):
    webhook_url = f'{get_ngrok_url()}/{secret}'

    await bot.set_webhook(webhook_url)


async def on_shutdown(dp):
    # insert code here to run it before shutdown
    pass

if __name__ == '__main__':
    webapp_host = 'localhost'
    webapp_port = get_port()

    start_webhook(
        dispatcher=dp, webhook_path=f'/{secret}',
        on_startup=on_startup, on_shutdown=on_shutdown,
        skip_updates=True, host=webapp_host, port=webapp_port
    )
