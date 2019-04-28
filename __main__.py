import datetime

import pytz
import telepot
import timeago
from flask import Flask, request

from config import API_TOKEN, secret
from gwevents import Events

# Initialize telegrambot and dispatcher
bot = telepot.Bot(API_TOKEN)
bot.setWebhook("https://Roald.pythonanywhere.com/{}".format(secret), max_connections=1)
events = Events()

app = Flask(__name__)

@app.route('/{}'.format(secret), methods=["POST"])
def telegram_webhook():
    update = request.get_json()
    if "message" in update:
        text = update["message"]["text"]
        chat_id = update["message"]["chat"]["id"]
        if '/start' in text or '/help' in text:
            send_welcome(chat_id)
        elif '/latest' in text:
            send_latest(chat_id)

    return "OK"


def send_welcome(chat_id):
    """
    This handler will be called when client send `/start` or `/help` commands.
    """
    bot.sendMessage(
        chat_id,
        'Get information on LIGO/Virgo gravitational wave events.\n'
        'Use /latest to see the latest event.')


def send_latest(chat_id):

    event = events.latest()
    event_type, confidence = events.get_event_type(event.name)
    confirmed = {'s': 'Unconfirmed', 'g': 'Confirmed'}

    bot.sendMessage(
        chat_id,
        f'*{event.name.upper()}*\n'
        f'{time_ago(event["created"])}\n\n'
        f'{confirmed[event.name[0].lower()]} {event_type} ({confidence:.2%}) event.',
        parse_mode='Markdown')
    try:
        image_fname = events.picture(event.name)
        with open(image_fname, 'rb') as picture:
            bot.sendPhoto(
                chat_id,
                picture
            )
    except FileNotFoundError:
        pass


def time_ago(dt):
    current_date = datetime.datetime.now(datetime.timezone.utc)

    return timeago.format(dt.to_pydatetime().replace(tzinfo=pytz.UTC), current_date)