import datetime
import logging

import timeago
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ParseMode

from config import API_TOKEN
from gwevents import Events

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize telegrambot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
events = Events()


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when client send `/start` or `/help` commands.
    """
    await message.reply(
        'Get information on LIGO/Virgo gravitational wave events.\n'
        'Use /latest to see the latest event.',
        reply=False)


@dp.message_handler(commands=['latest'])
async def send_latest(message: types.Message):

    event = events.latest()
    event_type, confidence = events.get_event_type(event.name)
    confirmed = {'s': 'Unconfirmed', 'g': 'Confirmed'}

    await bot.send_message(
        message.chat.id,
        f'*{event.name.upper()}*\n' +
        f'{time_ago(event["created"])}\n'
        f'{confirmed[event.name[0].lower()]} {event_type} ({confidence:.2%}) event.',
        parse_mode=ParseMode.MARKDOWN)
    try:
        image_fname = events.picture(event.name)
        with open(image_fname, 'rb') as picture:
            await bot.send_photo(
                message.chat.id,
                picture
            )
    except FileNotFoundError:
        pass


def time_ago(dt):
    current_date = datetime.datetime.now(datetime.timezone.utc)

    return timeago.format(dt.to_pydatetime(), current_date)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

