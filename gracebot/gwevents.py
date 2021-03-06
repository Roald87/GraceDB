import asyncio
import datetime
import logging
import urllib.error
import time
from typing import Dict

import dateutil.parser
import ligo.gracedb.exceptions
import timeago
from ligo.gracedb.rest import GraceDb

from image import ImageFromUrl
from voevent import VOEvent, VOEventFromEventId


class Events(object):
    """
    A dictionary with all superevents from the Grace database.
    """

    def __init__(self):
        self.client = GraceDb()
        self.data = {}
        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self._periodic_event_updater())

    def update_all(self):
        """
        Get the latest events from the Grace database.

        Returns
        -------
        None

        See Also
        --------
        https://gracedb.ligo.org/latest/
        """
        events = self.client.superevents(query="-ADVNO", orderby=["-created"])
        self.data = {}

        logging.info("Updating all events. This might take a minute.")
        start = time.time()
        for i, event in enumerate(events, 1):
            self._add_to_event_data(event)

        end = time.time()
        logging.info(f"Updating {i} events took {round(end - start, 2)} s.")

    def update_events_last_week(self):
        logging.info("Updating all events until 1 week ago. This might take a minute.")
        start = time.time()
        events = self.client.superevents(
            query="created: 1 week ago .. now -ADVNO", orderby=["-created"]
        )

        for i, event in enumerate(events, 1):
            logging.info(f"Updating event {event['superevent_id']}")
            self._add_to_event_data(event)

        end = time.time()
        logging.info(f"Updating {i} events took {round(end - start, 2)} s.")

    def update_single(self, event_id: str):
        """
        Update and store the data of a single event in the event dictionary.

        Parameters
        ----------
        event_id : str

        Returns
        -------

        """
        # Make sure the event id has the right upper and lower case format
        _event_id = event_id[0].upper() + event_id[1:].lower()

        start = time.time()
        try:
            event = self.client.superevent(_event_id)
            event = event.json()
        except (ligo.gracedb.exceptions.HTTPError, urllib.error.HTTPError) as e:
            logging.error(f"Could not find event {_event_id}. Exception: {e}")
            return
        end = time.time()
        logging.info(
            f"Updating single event from database took {round(end - start, 2)} s."
        )

        self._add_to_event_data(event)

    def _add_to_event_data(self, event):
        event_id = event.pop("superevent_id")
        event["created"] = dateutil.parser.parse(event["created"])
        self.data[event_id] = event

        self._add_event_info_from_voevent(event_id)

    def _add_event_info_from_voevent(self, event_id: str):
        voevent = VOEventFromEventId()
        try:
            voevent.get(event_id)
            self._add_event_distance(voevent)
            self._add_event_classification(voevent)
            self._add_instruments(voevent)
        except (ligo.gracedb.exceptions.HTTPError, urllib.error.HTTPError) as e:
            logging.warning(
                f"Couldn't get info from VOEvent file with event id {event_id}"
                f"Exception: {e}"
            )

    def _add_event_distance(self, voevent: VOEvent):
        """
        Add distance and its standard deviation to the event dictionary.

        Parameters
        ----------
        voevent : VOEvent

        Returns
        -------
        None
        """
        self.data[voevent.id]["distance_mean_Mly"] = voevent.distance
        self.data[voevent.id]["distance_std_Mly"] = voevent.distance_std

    def _add_event_classification(self, voevent: VOEvent):
        """
        Adds the event type to the events dictionary.

        Possible event types are binary black hole merger, black hole neutron
        star merger etc.

        Returns
        -------
        None
        """
        self.data[voevent.id]["event_types"] = voevent.p_astro
        self.data[voevent.id]["most_likely"] = self.get_likely_event_type(voevent.id)

    def _add_instruments(self, voevent: VOEvent):
        """

        Parameters
        ----------
        voevent

        Returns
        -------

        """
        self.data[voevent.id]["instruments_short"] = voevent.seen_by_short
        self.data[voevent.id]["instruments_long"] = voevent.seen_by_long

    async def _periodic_event_updater(self):
        """
        Fetches all the events from the GraceDB database.

        Returns
        -------
        None

        """
        while True:
            await asyncio.sleep(delay=36000)

            logging.info("Refreshing event database.")
            self.update_all()

    def get_likely_event_type(self, event_id: str) -> str:
        """
        Return the most likely event type of a certain event.

        Parameters
        ----------
        event_id : str
            The event ID you want to know the event type of.

        Returns
        -------
        str
            Most likely event type.
        """
        try:
            event_types = self.data[event_id]["event_types"]
            most_likely, _ = sorted(
                event_types.items(), key=lambda value: value[1], reverse=True
            )[0]
        except AttributeError:
            logging.error(f"Failed to get most likely event of {event_id}")
            return ""

        return most_likely

    @property
    def latest(self) -> Dict[str, dict]:
        """
        Return the latest event from the Grace database.

        Returns
        -------
        dict
            Latest event.
        """
        for id, info in self.data.items():
            return {id: info}

        return {"": dict()}

    def picture(self, event_id: str) -> str:
        """
        Return local path of an image from a specific event.

        Image priority is as follows: 1) LALInference 2) skymap 3) bayestar.png.

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

        for fname in ["LALInference", "skymap", "bayestar"]:
            link = get_latest_file_url(files, fname, ".png")
            if len(link) > 0:
                break

        if len(link) == 0:
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
    filtered_files = {
        fname: link
        for fname, link in files.items()
        if (starts_with in fname[: len(starts_with)])
        and file_extension in fname
        and "volume" not in fname
    }
    if len(filtered_files) == 0:
        return ""

    newest_file = sorted(filtered_files.keys())[-1]
    link = files.get(newest_file, "")

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
