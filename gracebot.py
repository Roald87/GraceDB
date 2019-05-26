import logging
from collections import Counter

from aiogram import Bot, types

from gwevents import Events, time_ago


class GraceBot(Bot):

    def __init__(self, token: str):
        super(GraceBot, self).__init__(token=token)
        self.events = Events()
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
            'Get information on LIGO/Virgo gravitational wave events.\n'
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
        event = self.events.latest()
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

        await self.send_message(message.chat.id, text, parse_mode='markdown')

        try:
            with open(self.events.picture(event.name), 'rb') as picture:
                await self.send_photo(message.chat.id, picture)
        except FileNotFoundError:
            logging.error("Couldn't find the event image")
            return None

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
        possible_BBH = event_counter['SBBH']
        confirmed_BNS = event_counter['GBNS']
        possible_BNS = event_counter['SBNS']
        confirmed_NSBH = event_counter['GNSBH']
        possible_NSBH = event_counter['SNSBH']
        terrestrial = event_counter['Sterrestrial']

        text = (
            f"Observational run 3 has detected {len(self.events.events)} "
            "events since April 1st 2019. (confirmed/most likely)\n\n"
            
            f"Binary black hole mergers: {confirmed_BBH}/{possible_BBH}.\n"
            f"Binary neutron star merger: {confirmed_BNS}/{possible_BNS}.\n"
            f"Neutron star black hole merger: {confirmed_NSBH}/{possible_NSBH}.\n"
            f"Likely terrestrial: {terrestrial}.\n"
        )

        await self.send_message(message.chat.id, text)
