import datetime
import os
import threading
import time
import traceback

import pytz
import telepot
import timeago
from flask import Flask, request

from config import API_TOKEN, remote, secret, tunnel
from gwevents import Events

app = Flask(__name__)
bot = telepot.Bot(API_TOKEN)

def is_running_locally():
    running_locally = False
    try:
        running_locally = os.environ['PYCHARM_HOSTED']
    except KeyError:
        running_locally = False

    return running_locally

if is_running_locally():
    secret = ''
    webhook_url = tunnel
else:
    webhook_url = remote

bot.setWebhook(webhook_url, max_connections=1)


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


def every(delay: int, task: object):
    """
    Repeat a task at an interval.

    Parameters
    ----------
    delay : int
        Calls the task with this interval in seconds.
    task : object
        The task which should be called.

    Returns
    -------
    None

    See Also
    --------
    https://stackoverflow.com/a/49801719/6329629
    """
    next_time = time.time() + delay
    while True:
        time.sleep(max(0, next_time - time.time()))
        try:
            task()
            print("updating events")
        except Exception:
            traceback.print_exc()
    # skip tasks if we are behind schedule:
    next_time += (time.time() - next_time) // delay * delay + delay


events = Events()
hourly_event_updater = threading.Thread(target=lambda: every(3600, events.update_events))
hourly_event_updater.start()


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

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8088, debug=True)