import logging
from collections import Counter

from aiogram import Bot, types

from gwevents import Events, time_ago
from permanentset import PermanentSet


class GraceBot(Bot):
    def __init__(self, token: str):
        super(GraceBot, self).__init__(token=token)
        self.events = Events()
        self.subscribers = PermanentSet("gracebot/subscribers.txt")
        self.event_types = {
            # Probability that the source is a binary black hole merger (both
            # objects heavier than 5 solar masses)
            "BBH": "binary black hole merger",
            # Probability that the source is a binary neutron star merger
            # (both objects lighter than 3 solar masses)
            "BNS": "binary neutron star merger",
            # Probability that the source is a neutron star-black hole merger
            # (primary heavier than 5 solar masses, secondary lighter than 3
            # solar masses)
            "NSBH": "neutron star black hole merger",
            # Probability that the source is terrestrial(i.e., a background
            # noise fluctuation or a glitch)
            "Terrestrial": "terrestrial",
            # Probability that the source has at least one object between 3 and
            # 5 solar masses
            "MassGap": "mass gap",
        }

    async def send_preliminary(self, message):
        self.events.update_all_events()

        text = f"A new event has been measured!"
        event_id = list(self.events.events.keys())[0]
        await self._send_event_info_to_all_users(event_id, text)

    async def send_update(self, message):
        event_id = event_id_from_message(message)
        self.events.update_single_event(event_id)

        text = f"Event {event_id} has been updated."
        await self._send_event_info_to_all_users(event_id, text)

    async def send_retraction(self, message):
        event_id = event_id_from_message(message)
        text = f"Event {event_id} has been retracted. The event details were:"

        await self._send_event_info_to_all_users(event_id, text)

        self.events.update_all_events()

    async def _send_event_info_to_all_users(self, event_id: str, text: str) -> None:
        for user_id in self.subscribers.data:
            await self.send_message(user_id, text)
            await self.send_event_info(user_id, event_id)

    async def send_event_info(self, chat_id: str, event_id: str) -> None:
        """
        Send information of a specific event to the user.

        Parameters
        ----------
        chat_id : str
            Where to send the message to.
        event_id : str
            The event to send the information about.

        Returns
        -------
        None
        """
        event = self.events.events[event_id]

        text = f"*{event_id.upper()}*\n" f'{time_ago(event["created"])}\n\n'

        try:
            event_type = self.events.get_likely_event_type(event_id)
            confidence = self.events.events[event_id]["event_types"][event_type]
            text += (
                f"Unconfirmed {self.event_types[event_type]} ({confidence:.2%}) event."
            )

            distance_mean = round(event["distance_mean_Mly"] / 1000, 2)
            distance_std = round(event["distance_std_Mly"] / 1000, 2)
            text = (
                text[:-1] + f" at {distance_mean} ± {distance_std} billion light years."
            )
        except KeyError:
            pass

        await self.send_message(chat_id, text, parse_mode="markdown")

        try:
            with open(self.events.picture(event_id), "rb") as picture:
                await self.send_photo(chat_id, picture)
        except FileNotFoundError:
            logging.error("Couldn't find the event image")
            return None

    async def send_welcome_message(self, message: types.Message) -> None:
        """
        Send a welcome message to the user.

        Parameters
        ----------
        message : aiogram.types.Message
            The message send by the user.

        Returns
        -------
        None.
        """
        text = (
            "Get information on LIGO/Virgo gravitational wave events.\n\n"
            "Use /latest to see the latest event, or see an overview of all "
            "O3 events with /stats."
        )

        await self.send_message(message.chat.id, text)

    async def send_latest(self, message: types.Message) -> None:
        """
        Send some details of the most recent gravitational wave event.

        Parameters
        ----------
        message : aiogram.types.Message
            The message send by the user.

        Returns
        -------
        None.
        """
        event_id = list(self.events.latest)[0]

        await self.send_event_info(message, event_id)

    async def send_o3_stats(self, message: types.Message) -> None:
        """
        Send some statistics of observational run 3 (O3).

        Parameters
        ----------
        message : aiogram.types.Message
            The message send by the user.

        Returns
        -------
        None.
        """
        # TODO take confirmed from other source since it will not be updated
        # in graceDB if they are confirmed. For that use:
        # https://www.gw-openscience.org/catalog/GWTC-1-confident/html/
        event_counter = Counter(
            [info["most_likely"] for info in self.events.events.values()]
        )

        unconfirmed_bbh = event_counter["BBH"]
        unconfirmed_bns = event_counter["BNS"]
        unconfirmed_nsbh = event_counter["NSBH"]
        unconfirmed_mg = event_counter["MassGap"]
        terrestrial = event_counter["Terrestrial"]

        text = (
            f"Observational run 3 has detected *{len(self.events.events)}* "
            "events since April 1st 2019.\n\n"
            ""
            "Event types (confirmed/unconfirmed)\n"
            f"Binary black hole mergers: {0}/{unconfirmed_bbh}.\n"
            f"Binary neutron star mergers: {0}/{unconfirmed_bns}.\n"
            f"Neutron star black hole mergers: {0}/{unconfirmed_nsbh}.\n"
            f"At least one object between 3 and 5 solar masses: {0}/{unconfirmed_mg}.\n"
            f"Likely terrestrial: {terrestrial}.\n"
        )

        await self.send_message(message.chat.id, text, parse_mode="markdown")

    async def add_subscriber(self, message: types.Message):
        """
        Add the user from the message to the subscriber list.

        Parameters
        ----------
        message : aiogram.types.Message
            The message send by the user.

        Returns
        -------
        None.
        """
        user_id = message.chat.id
        if self.subscribers.is_in_list(user_id):
            await self.send_message(user_id, "You are already subscribed.")
        else:
            self.subscribers.add(message.chat.id)
            await self.send_message(
                user_id, "You will now receive the latest event updates."
            )

    async def remove_subscriber(self, message: types.Message):
        """
        Remove the user from the message from the subscriber list.

        Parameters
        ----------
        message : aiogram.types.Message
            The message send by the user.

        Returns
        -------
        None.
        """
        user_id = message.chat.id
        if not self.subscribers.is_in_list(user_id):
            await self.send_message(user_id, "You are not subscribed.")
        else:
            self.subscribers.remove(message.chat.id)
            await self.send_message(
                user_id, "You will no longer receive the latest event updates."
            )


def event_id_from_message(message: types.Message) -> str:
    """
    Return the event id which is assumed to come right after the command.

    Parameters
    ----------
    message : aiogram.types.Message
        The message send by the user.

    Returns
    -------
    The event id.
    """
    try:
        event_id = message.text.split(" ")[-1]
    except KeyError:
        event_id = None

    return event_id