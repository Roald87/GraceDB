import logging
from collections import Counter

from aiogram import Bot, types

from gwevents import Events, time_ago


class GraceBot(Bot):

    def __init__(self, token: str):
        super(GraceBot, self).__init__(token=token)
        self.events = Events()
        # self.subscribers = PermanentSet('subscribers.txt')
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
        self.events.update_events()

        text = f"A new event has been measured!"
        chat_id = 34702149
        await self.send_message(chat_id, text)
        await self.send_latest(message, chat_id=chat_id)

    async def send_update(self, message):
        # self.events.update_events()

        _event_id = message.text.split(' ')[-1]
        text = f"Event {_event_id} has been updated."
        chat_id = 34702149
        await self.send_message(chat_id, text)

    async def send_retraction(self, message):
        # self.events.update_events()
        _event_id = message.text.split(' ')[-1]
        text = f"Event {_event_id} has been retracted."
        chat_id = 34702149
        await self.send_message(chat_id, text)

    async def send_event_info(self, message: types.Message, event_id: str, chat_id:str=None) -> \
            None:
        event = self.events.events.loc[event_id]
        text = (
            f'*{event.name.upper()}*\n'
            f'{time_ago(event["created"])}\n\n')

        try:
            event_type, confidence = self.events.get_likely_event_type(event.name)
            confirmation_states = {'s': 'Unconfirmed', 'g': 'Confirmed'}
            confirmation_state = confirmation_states[event.name[0].lower()]
            text += f'{confirmation_state} {self.event_types[event_type]} ({confidence:.2%}) event.'

            distance_mean = round(event["distance_mean_Mly"] / 1000, 2)
            distance_std = round(event["distance_std_Mly"] / 1000, 2)
            text = text[:-1] + f' at {distance_mean} ± {distance_std} billion light years.'
        except KeyError:
            pass

        _chat_id = chat_id if chat_id else message.chat.id
        await self.send_message(_chat_id, text, parse_mode='markdown')

        try:
            with open(self.events.picture(event.name), 'rb') as picture:
                await self.send_photo(_chat_id, picture)
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

    async def send_latest(self, message: types.Message, chat_id: str=None) -> None:
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
        event = self.events.latest()
        await self.send_event_info(message, event.name, chat_id)

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
        event_counter = Counter([
            _id[0] + _type
            for _id, _type in self.events.events['most_likely'].items()
            if _id and _type])

        confirmed_BBH = event_counter['GBBH']
        unconfirmed_BBH = event_counter['SBBH']
        confirmed_BNS = event_counter['GBNS']
        unconfirmed_BNS = event_counter['SBNS']
        confirmed_NSBH = event_counter['GNSBH']
        unconfirmed_NSBH = event_counter['SNSBH']
        terrestrial = event_counter['STerrestrial']

        text = (
            f"Observational run 3 has detected *{len(self.events.events)}* "
            "events since April 1st 2019.\n\n"
            ""
            "Event types (confirmed/unconfirmed)\n"
            f"Binary black hole mergers: {confirmed_BBH}/{unconfirmed_BBH}.\n"
            f"Binary neutron star mergers: {confirmed_BNS}/{unconfirmed_BNS}.\n"
            f"Neutron star black hole mergers: {confirmed_NSBH}/{unconfirmed_NSBH}.\n"
            f"Likely terrestrial: {terrestrial}.\n"
        )

        await self.send_message(message.chat.id, text, parse_mode='markdown')
