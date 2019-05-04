import threading
import time
import traceback

import gcn
import telepot

from config import API_TOKEN, get_webhook_url
from gwevents import Events, time_ago
from permanentset import PermanentSet


class GraceBot(object):

    def __init__(self):
        self.bot = telepot.Bot(API_TOKEN)
        self.bot.setWebhook(get_webhook_url(), max_connections=1)
        self.subscribers = PermanentSet('subscribers.txt')
        self.events = Events()
        hourly_event_updater = threading.Thread(
            target=lambda: every(3600, self.events.update_events))
        hourly_event_updater.start()

    @gcn.handlers.include_notice_types(gcn.notice_types.LVC_PRELIMINARY)
    def _process_gcn_preliminary(self, payload, root):
        subscribers = self.subscribers.read()
        for subscriber in subscribers:
            self.bot.sendMessage(subscriber, "A new preliminairy event was added!")

        self.events.update_events()

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
            'Get information on LIGO/Virgo gravitational wave events.\n\n'
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

    def add_subscriber(self, chat_id: int):
        if self.subscribers.is_in_list(chat_id):
            self.bot.sendMessage(chat_id, "You are already subscribed. Use /unsubscribe to "
                                          "unsubscribe.")
        else:
            self.subscribers.add(chat_id)
            self.bot.sendMessage(chat_id, "You'll now receive the latest event updates!")

    def remove_subscriber(self, chat_id: int):
        if not self.subscribers.is_in_list(chat_id):
            self.bot.sendMessage(chat_id, "It looks like you are not subscribed. Use /subscribe "
                                          "to subscribe.")
        else:
            self.subscribers.remove(chat_id)
            self.bot.sendMessage(chat_id, "You've been removed from the event update list.")


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