import datetime
import logging

import timeago
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ParseMode

from config import API_TOKEN
from gwevents import Events

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
events = Events()


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when client send `/start` or `/help` commands.
    """
    await message.reply(
        "I'll show you the latest LIGO/Virgo gravitational wave events.",
        reply=False)


@dp.message_handler(commands=['latest'])
async def send_latest(message: types.Message):

    event = events.latest()

    await bot.send_message(
        message.chat.id,
        f'*{event.name.upper()}*\n' +
        f'{time_ago(event["created"])}',
        parse_mode=ParseMode.MARKDOWN)


def time_ago(dt):
    current_date = datetime.datetime.now(datetime.timezone.utc)

    return timeago.format(dt.to_pydatetime(), current_date)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

