import logging

from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook

from config import (
    API_TOKEN,
    logging_kwargs,
    preliminary_command,
    retraction_command,
    secret,
    update_command,
)
from gracebot import GraceBot
from ngrok import get_ngrok_url, get_port

logging.basicConfig(**logging_kwargs)

bot = GraceBot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start", "help"])
async def send_welcome(message: types.Message):
    await bot.send_welcome_message(message)


@dp.message_handler(commands=["latest"])
async def send_latest_event(message: types.Message):
    await bot.send_latest(message)


@dp.message_handler(commands=["stats"])
async def send_o3_stats(message: types.Message):
    await bot.send_o3_stats(message)


@dp.message_handler(commands=["subscribe"])
async def add_subscriber(message: types.Message):
    await bot.add_subscriber(message)


@dp.message_handler(commands=["unsubscribe"])
async def remove_subscriber(message: types.Message):
    await bot.remove_subscriber(message)


@dp.message_handler(commands=[preliminary_command])
async def send_preliminary(message: types.Message):
    await bot.send_preliminary(message)


@dp.message_handler(commands=[update_command])
async def send_update(message: types.Message):
    await bot.send_update(message)


@dp.message_handler(commands=[retraction_command])
async def send_retraction(message: types.Message):
    await bot.send_retraction(message)


async def on_startup(dp):
    webhook_url = f"{get_ngrok_url()}/{secret}"
    await bot.set_webhook(webhook_url)


if __name__ == "__main__":
    webapp_host = "localhost"
    webapp_port = get_port()

    start_webhook(
        dispatcher=dp,
        webhook_path=f"/{secret}",
        on_startup=on_startup,
        skip_updates=True,
        host=webapp_host,
        port=webapp_port,
    )
