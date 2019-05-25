import logging

from aiogram import Bot, types

from gwevents import Events, time_ago


class GraceBot(Bot):

    def __init__(self, token: str):
        super(GraceBot, self).__init__(token=token)
        self.events = Events()

    async def send_welcome_message(self, message: types.Message) -> None:
        """
        Sends a welcome message to the user.

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
            'Use /latest to see the latest event.')

        await self.send_message(message.chat.id, text)

    async def send_latest(self, message: types.Message) -> None:
        """
        Sends some details of the most recent gravitational wave event.

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
            text += f'{confirmation_state} {event_type} ({confidence:.2%}) event.'

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
