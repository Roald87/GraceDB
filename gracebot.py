import time
import traceback

import gevent
import telepot

from config import API_TOKEN, get_webhook_url
from gwevents import Events, time_ago


class GraceBot(object):

    def __init__(self):
        self.bot = telepot.Bot(API_TOKEN)
        self.bot.setWebhook(get_webhook_url(), max_connections=1)
        self.events = Events()
        run_regularly(self.events.update_events(), 10)

    def send_welcome(self, chat_id: int) -> None:
        """
        Welcome and help message of the bot.

        Parameters
        ----------
        chat_id : int
            Chat to send the message to.

        Returns
        -------
        None
        """
        self.bot.sendMessage(
            chat_id,
            'Get information on LIGO/Virgo gravitational wave events.\n'
            'Use /latest to see the latest event.')

    def send_latest(self, chat_id: int) -> None:
        """
        Send the latest event to the telegram bot.

        Parameters
        ----------
        chat_id : int

        Returns
        -------
        None
        """

        event = self.events.latest()
        distance_mean = round(event["distance_mean_Mly"])
        distance_std = round(event["distance_std_Mly"])
        event_type, confidence = self.events.get_event_type(event.name)
        confirmed = {'s': 'Unconfirmed', 'g': 'Confirmed'}

        self.bot.sendMessage(
            chat_id,
            f'*{event.name.upper()}*\n'
            f'{time_ago(event["created"])}\n\n'
            f'{confirmed[event.name[0].lower()]} {event_type} ({confidence:.2%}) event '
            f'at {distance_mean} ± {distance_std} million light years.',
            parse_mode='Markdown')
        try:
            image_fname = self.events.picture(event.name)
            with open(image_fname, 'rb') as picture:
                self.bot.sendPhoto(
                    chat_id,
                    picture
                )
        except FileNotFoundError:
            pass

def run_regularly(function, interval, *args, **kwargs):
    '''

    Parameters
    ----------
    function
    interval
    args
    kwargs

    Returns
    -------

    See Also
    --------
    https://stackoverflow.com/a/26549002/6329629
    '''
    while True:
        gevent.sleep(interval)
        function(*args, **kwargs)

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