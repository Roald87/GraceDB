from aiogram import Bot

from gwevents import Events, time_ago


class GraceBot(Bot):

    def __init__(self, token):
        super(GraceBot, self).__init__(token=token)
        self.events = Events()


    @property
    def welcome_message(self) -> str:
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
        return (
            'Get information on LIGO/Virgo gravitational wave events.\n'
            'Use /latest to see the latest event.')

    @property
    def latest_message(self) -> str:
        """
        Return message with info of the latest event.

        Returns
        -------
        None
        """

        event = self.events.latest()
        message = (
            f'*{event.name.upper()}*\n'
            f'{time_ago(event["created"])}\n\n')

        try:
            event_type, confidence = self.events.get_event_type(event.name)
            confirmation_states = {'s': 'Unconfirmed', 'g': 'Confirmed'}
            confirmation_state = confirmation_states[event.name[0].lower()]
            message +=  f'{confirmation_state} {event_type} ({confidence:.2%}) event.'

            distance_mean = round(event["distance_mean_Mly"]/1000, 2)
            distance_std = round(event["distance_std_Mly"]/1000, 2)
            message = message[:-1] + f' at {distance_mean} ± {distance_std} billion light years.'
        except KeyError:
            pass

        return message



    def latest_image(self) -> str:
        event = self.events.latest()
        try:
            return self.events.picture(event.name)
        except FileNotFoundError:
            return None