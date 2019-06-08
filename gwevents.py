import asyncio
import datetime
import logging

import dateutil.parser
import timeago
from ligo.gracedb.rest import GraceDb

from functions import progress_bar
from image import ImageFromUrl
from voevent import VOEvent


class Events(object):
    """
    A dictionary with all superevents from the Grace database.
    """

    def __init__(self):
        self.client = GraceDb()
        self.events = {}
        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self._periodic_event_updater())

    def update_events(self):
        """
        Get the latest events from the Grace database.

        Returns
        -------
        None

        See Also
        --------
        https://gracedb.ligo.org/latest/
        """
        logging.info("Getting the latest events.")
        _events = self.client.superevents(query='Production', orderby=['-created'])

        self.events = {}
        for _event in _events:
            # ADVNO = advocate says event is not ok.
            if 'ADVNO' not in _event['labels']:
                _event_id = _event.pop('superevent_id')
                _event['created'] = dateutil.parser.parse(_event['created'])
                self.events[_event_id] = _event

        #TODO only take last three events for testing. Remove for master.
        self.events = {k:v for i, (k, v) in enumerate(self.events.items()) if i < 3}

        self._add_possible_event_types()
        self._add_event_distances()

    def _add_event_distances(self):
        """
        Adds the event distances to the event data frame.

        Returns
        -------
        None
        """
        logging.info("Getting event distances.")

        for i, _event_id in enumerate(self.events.keys(), 1):
            progress_bar(i, len(self.events), "Event distances")

            self._add_event_distance(_event_id)

    def _add_event_distance(self, event_id: str):
        """
        Add distance and its standard deviation to the event DataFrame

        Parameters
        ----------
        event_id :str

        Returns
        -------
        None
        """
        voevent = VOEvent()
        voevent.from_event_id(event_id)

        self.events[event_id]['distance_mean_Mly'] = voevent.distance
        self.events[event_id]['distance_std_Mly'] = voevent.distance_std

    def _add_possible_event_types(self):
        """
        Adds the event type to the events data frame.

        Possible event types are binary black hole merger, black hole neutron
        star merger etc.

        Returns
        -------
        None
        """
        logging.info("Getting possible event types.")
        for i, _event_id in enumerate(self.events.keys(), 1):
            progress_bar(i, len(self.events), "Event types")

            voevent = VOEvent()
            voevent.from_event_id(_event_id)

            self.events[_event_id]['event_types'] = voevent.p_astro
            self.events[_event_id]['most_likely'] = \
                self.get_likely_event_type(_event_id)

    async def _periodic_event_updater(self):
        """
        Fetches all the events from the GraceDB database.

        Returns
        -------
        None

        """
        while True:
            logging.info("Refreshing event database.")
            self.update_events()

            await asyncio.sleep(delay=3600)

    def get_likely_event_type(self, event_id: str) -> float:
        """
        Return the most likely event type of a certain event.

        Parameters
        ----------
        event_id : str
            The event ID you want to know the event type of.

        Returns
        -------
        tuple
            Most likely event type.
        """
        try:
            event_types = self.events[event_id]['event_types']
            most_likely, _ = sorted(
                event_types.items(), key=lambda value: value[1], reverse=True)[0]
        except AttributeError:
            logging.error(f"Failed to get most likely event of {event_id}")
            return None

        return most_likely

    @property
    def latest(self) -> dict:
        """
        Return the latest event from the Grace database.

        Returns
        -------
        dict
            Latest event.
        """
        for _id, _info in self.events.items():
            return {_id: _info}

    def picture(self, event_id: str) -> str:
        """
        Return local path of an image from a specific event.

        Currently takes the bayestar.png image. Maybe changes in the future
        when more images come available.

        Parameters
        ----------
        event_id : str
            The name of the event you want to have a picture of.

        Returns
        -------
        str
            Local path of the image.
        """
        files = self.client.files(event_id).json()
        link = get_latest_file_url(files, 'bayestar', '.png')

        if link is None:
            raise FileNotFoundError
        else:
            img = ImageFromUrl(link)

        return img.path


def get_latest_file_url(files: dict, starts_with: str, file_extension: str) -> str:
    """
    Get the url to a file which should start and have a specific file extension.

    Parameters
    ----------
    files : dict
        Keys are the filenames and the values are the urls.
    starts_with : str
        Start of the filename.
    file_extension : str
        End of the filename. For example the file extension.

    Returns
    -------
    str
        URL of the most recent file.
    """
    filtered_files = {fname: link for fname, link in files.items()
                      if (starts_with in fname[:len(starts_with)])
                      and file_extension in fname
                      and 'volume' not in fname}
    newest_file = sorted(filtered_files.keys())[-1]
    link = files.get(newest_file, None)

    return link


def time_ago(dt: datetime.datetime) -> str:
    """
    When a datetime took place, e.g. 1 hour ago, 2 days ago, in 3 weeks.

    Parameters
    ----------
    dt : datetime.datetime
        Date to show how when it took place.

    Returns
    -------
    str
        When the datetime will occur or occurred.
    """
    current_date = datetime.datetime.now(datetime.timezone.utc)

    return timeago.format(dt, current_date)

if __name__ == '__main__':
    events = Events()
    events.update_events()