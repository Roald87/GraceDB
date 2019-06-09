import logging
from collections import Counter

from aiogram import Bot, types

from gwevents import Events, time_ago
from permanentset import PermanentSet


class GraceBot(Bot):

    def __init__(self, token: str):
        super(GraceBot, self).__init__(token=token)
        self.events = Events()
        self.subscribers = PermanentSet('subscribers.txt')
        self.event_types = {
            # Probability that the source is a binary black hole merger (both
            # objects heavier than 5 solar masses)
            'BBH': 'binary black hole merger',
            # Probability that the source is a binary neutron star merger
            # (both objects lighter than 3 solar masses)
            'BNS': 'binary neutron star merger',
            # Probability that the source is a neutron star-black hole merger
            # (primary heavier than 5 solar masses, secondary lighter than 3
            # solar masses)
            'NSBH': 'neutron star black hole merger',
            # Probability that the source is terrestrial(i.e., a background
            # noise fluctuation or a glitch)
            'Terrestrial': 'terrestrial',
            # Probability that the source has at least one object between 3 and
            # 5 solar masses
            'MassGap': 'mass gap',
        }

    async def send_preliminary(self, message):
        self.events.update_all_events()

        text = f"A new event has been measured!"

        for user_id in self.subscribers:
            message.chat.id = user_id
            await self.send_message(message.chat.id, text)
            await self.send_latest(message)

    async def send_update(self, message):
        _event_id = event_id_from_message(message)
        self.events.update_single_event(_event_id)

        text = f"Event {_event_id} has been updated."

        for user_id in self.subscribers:
            message.chat.id = user_id
            await self.send_message(message.chat.id, text)
            await self.send_event_info(message, _event_id)

    async def send_retraction(self, message):
        _event_id = event_id_from_message(message)
        text = f"Event {_event_id} has been retracted. " \
            f"The event details were:"

        for user_id in self.subscribers:
            message.chat.id = user_id
            await self.send_message(message.chat.id, text)
            await self.send_event_info(message, _event_id)

        self.events.update_all_events()

    async def send_event_info(self, message: types.Message, event_id: str) -> None:
        """
        Send information of a specific event to the user.

        Parameters
        ----------
        message : aiogram.types.Message
            The message send by the user.
        event_id : str
            Send information about this event to the user.

        Returns
        -------
        None
        """
        event = self.events.events[event_id]

        text = (
            f'*{event_id.upper()}*\n'
            f'{time_ago(event["created"])}\n\n')

        try:
            event_type = self.events.get_likely_event_type(event_id)
            confidence = self.events.events[event_id]['event_types'][event_type]
            text += f'Unconfirmed {self.event_types[event_type]} ({confidence:.2%}) event.'

            distance_mean = round(event["distance_mean_Mly"] / 1000, 2)
            distance_std = round(event["distance_std_Mly"] / 1000, 2)
            text = text[:-1] + f' at {distance_mean} ± {distance_std} billion light years.'
        except KeyError:
            pass

        await self.send_message(message.chat.id, text, parse_mode='markdown')

        try:
            with open(self.events.picture(event_id), 'rb') as picture:
                await self.send_photo(message.chat.id, picture)
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
            'Get information on LIGO/Virgo gravitational wave events.\n\n'
            'Use /latest to see the latest event, or see an overview of all '
            'O3 events with /stats.')

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
        _event_id = list(self.events.latest)[0]

        await self.send_event_info(message, _event_id)

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
        event_counter = Counter([
            _info['most_likely']
            for _info in self.events.events.values()])

        unconfirmed_bbh = event_counter['BBH']
        unconfirmed_bns = event_counter['BNS']
        unconfirmed_nsbh = event_counter['NSBH']
        unconfirmed_mg = event_counter['MassGap']
        terrestrial = event_counter['Terrestrial']

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

        await self.send_message(message.chat.id, text, parse_mode='markdown')

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
        _event_id = message.text.split(' ')[-1]
    except KeyError:
        _event_id = None

    return _event_id
