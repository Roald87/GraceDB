import logging
from collections import Counter, defaultdict

import aiogram
from aiogram import Bot, types
from aiogram.utils.emoji import emojize

from detector import Detector
from gwevents import Events, time_ago
from keyboard import InlineKeyboard
from permanentset import PermanentSet


class GraceBot(Bot):
    def __init__(self, token: str):
        super().__init__(token=token)
        self.events: Events = Events()
        self.events.update_all()
        self.event_keyboards: dict = defaultdict(InlineKeyboard)
        self.new_event_messages_send: PermanentSet = PermanentSet(
            "new_event_messages_send.txt", str
        )
        self.subscribers: PermanentSet = PermanentSet("subscribers.txt", int)
        self.event_types: dict = {
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
        self.events.update_all()

        event_id = list(self.events.events.all_keys())[0]
        if event_id in self.new_event_messages_send.data:
            return
        else:
            self.new_event_messages_send.add(event_id)

        text = f"A new event has been measured!\n\n"
        await self._send_event_info_to_all_users(event_id, text)

    async def send_update(self, message):
        event_id = event_id_from_message(message)
        self.events.update_single(event_id)

        text = f"Event {event_id} has been updated.\n\n"
        await self._send_event_info_to_all_users(event_id, text)

    async def send_retraction(self, message):
        event_id = event_id_from_message(message)
        text = f"Event {event_id} has been retracted. The event details were:\n\n"

        await self._send_event_info_to_all_users(event_id, text)

        self.events.update_all()

    async def _send_event_info_to_all_users(self, event_id: str, pre_text: str) -> None:
        for user_id in self.subscribers.data:
            try:
                await self.send_event_info(user_id, event_id, pre_text)
            except aiogram.utils.exceptions.BotBlocked:
                logging.info(f"User {user_id} has blocked the bot.")
                continue

    async def send_event_info(
        self, chat_id: str, event_id: str, pre_text: str = ""
    ) -> None:
        """
        Send information of a specific event to the user.

        Parameters
        ----------
        chat_id : str
            Where to send the message to.
        event_id : str
            The event to send the information about.
        pre_text : str
            Will be added to the beginning of the message.

        Returns
        -------
        None
        """
        event = self.events.events[event_id]

        link = f"https://gracedb.ligo.org/superevents/{event_id}/view/"
        text = (
            pre_text + f"*{event_id.upper()}*\n" + f"{time_ago(event['created'])}\n\n"
        )

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

            instruments = self.events.events[event_id]["instruments_long"]
            text += f" The event was measured by {inline_list(instruments)}."
        except KeyError:
            pass

        text += f"\n\n[Event page]({link})"

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
            "Stay up-to-date on LIGO/Virgo gravitational wave events!\n"
            "\n"
            "You can /subscribe to automatically receive a message whenever a new event is "
            "measured, or an existing event is updated. Use /unsubscribe to stop receiving "
            "messages.\n"
            "\n"
            "Furthermore you can check out the /latest event, or select a past /event. "
            "Use /stats to see and overview of all O3 events or view the live detector /status."
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

        await self.send_event_info(message.chat.id, event_id)

    @property
    def event_keys(self) -> list:
        return [
            f"{id}_{info['most_likely']}" for id, info in self.events.events.items()
        ]

    async def send_event_selector(self, message: types.Message) -> None:
        """
        User can select any event from the O3 run and get a message with the details.

        Parameters
        ----------
        message : types.Message

        Returns
        -------
        None
        """
        self.event_keyboards[message.chat.id] = InlineKeyboard(
            self.event_keys, rows=1, columns=2
        )

        await self.send_message(
            chat_id=message.chat.id,
            text="Select the event you want to see the details of.",
            reply_markup=self.event_keyboards[message.chat.id],
        )

    async def event_selector_callback_handler(self, query: types.CallbackQuery) -> None:
        """
        This is called when the user presses a button to select an event.

        Parameters
        ----------
        query : types.CallbackQuery
            Callback query which contains info on which message the InlineKeyboard is
            attached to.

        Returns
        -------
        None
        """
        await query.answer()  # send answer to close the rounding circle

        answer_data = query.data
        logging.debug(f"answer_data={answer_data}")

        user_id = query.from_user.id
        valid_event_ids = self.event_keyboards[user_id].visible_keys
        if answer_data in valid_event_ids:
            event_id, _ = answer_data.split("_")
            await self.send_event_info(user_id, event_id)
        else:
            await self.event_keyboards[user_id].update(query)

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
            "*Event types*\n"
            f"Binary black hole mergers: *{unconfirmed_bbh}*.\n"
            f"Binary neutron star mergers: *{unconfirmed_bns}*.\n"
            f"Neutron star black hole mergers: *{unconfirmed_nsbh}*\n"
            f"At least one object between 3 and 5 solar masses: *{unconfirmed_mg}*.\n"
            f"Likely terrestrial (false alarm): *{terrestrial}*.\n"
        )

        await self.send_message(message.chat.id, text, parse_mode="markdown")

    async def send_detector_status(self, message: types.Message) -> None:
        """
        Send status of all three detectors to the user.

        Parameters
        ----------
        message : types.Message
            The message send by the user.

        Returns
        -------
        None
        """
        detectors = [Detector("Hanford"), Detector("Livingston"), Detector("Virgo")]

        detector_status = []
        for detector in detectors:
            hours = detector.status_duration.days * 24 + (
                detector.status_duration.seconds // 3600
            )
            minutes = (detector.status_duration.seconds % 3600) // 60

            detector_status.append(
                f"{emojize(detector.status_icon)} {detector.name}: "
                f"{detector.status} {hours}h {minutes}m"
            )
        text = "\n".join(detector_status)

        await self.send_message(message.chat.id, text)

    async def add_subscriber(self, message: types.Message) -> None:
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

    async def remove_subscriber(self, message: types.Message) -> None:
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


def inline_list(items):
    if len(items) == 0:
        return ""
    elif len(items) == 1:
        return items[0]
    else:
        return ", ".join(items[:-1]) + f" and {items[-1]}"
