import asyncio
import datetime
import logging

import ligo
import pandas as pd
import pytz
import timeago
from astropy.io import fits
from ligo.gracedb.rest import GraceDb

from functions import progress_bar
from image import ImageFromUrl
from voevent import VOEvent


class Events(object):
    """
    Holds a pandas DataFrame with all superevents from the Grace database.
    """

    def __init__(self):
        self.client = GraceDb()
        self.events = pd.DataFrame()
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
        events = self.client.superevents(query='Production', orderby=['-created'])

        df = pd.DataFrame()
        for i, event in enumerate(events, 1):
            event.pop('links')
            labels = event.pop('labels')
            # ADVNO = advocate says event is not ok.
            if 'ADVNO' not in labels:
                df = df.append({**event, 'labels': [labels]}, ignore_index=True)
        df.set_index('superevent_id', inplace=True)
        df['created'] = pd.to_datetime(df['created'])

        self.events = df.iloc[:3]

        self._add_possible_event_types()
        self._add_most_likely_event_types()
        self._add_event_distances()

    def _add_event_distances(self):
        """
        Adds the event distances to the event data frame.

        Returns
        -------
        None
        """
        logging.info("Getting event distances.")
        self.events = self.events.reindex(
            columns=list(self.events) + ['distance_mean_Mly', 'distance_std_Mly'])

        for i, (event_name, _) in enumerate(self.events.iterrows(), 1):
            progress_bar(i, len(self.events), "Event distances")

            filenames_with_url = self.client.files(event_name).json()
            try:
                fit_url = get_latest_file_url(filenames_with_url, 'bayestar', '.fits')
                with fits.open(fit_url) as fit_data:
                    self.events.at[event_name, 'distance_mean_Mly'] = \
                        mpc_to_mly(fit_data[1].header['DISTMEAN'])
                    self.events.at[event_name, 'distance_std_Mly'] = \
                        mpc_to_mly(fit_data[1].header['DISTSTD'])
            except ligo.gracedb.exceptions.HTTPError:
                pass

    def _add_most_likely_event_types(self) -> None:
        """
        Adds the most likely event types to the event dataframe.

        Returns
        -------
        None.
        """
        logging.info("Getting most likely event types.")
        _most_likely = pd.Series(name='most_likely')
        for i, (event_name, _) in enumerate(self.events.iterrows(), 1):
            _most_likely[event_name], _ = self.get_likely_event_type(event_name)

        self.events = pd.concat([self.events, _most_likely], axis=1)

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
        _all_types = pd.Series(name='event_types')
        for i, (event_name, _) in enumerate(self.events.iterrows(), 1):
            progress_bar(i, len(self.events), "Event types")

            try:
                event_type = self._pastro_from_vo_event(event_name)
            except ligo.gracedb.exceptions.HTTPError:
                logging.error(f"Failed to get event types of {event_name}")
                event_type = None
                pass
            _all_types[event_name] = event_type

        self.events = pd.concat([self.events, _all_types], axis=1)

    def _pastro_from_vo_event(self, event_id: str) -> dict:
        """
        Return event types from VOEvent xml which are also stored in `p_astro.json`.

        For event 'S190510g' the latest `p_astro.json` didn't match with the
        VOEvent xml file. The xml file contained more recent numbers. Therefore I
        made this method.

        Parameters
        ----------
        event_id : str
            The super event you want to get the event classification of.

        Returns
        -------
        dict
            Containing the same info as the `p_astro.json`.
        """

        voevent = VOEvent()
        voevent.from_event_id(event_id)

        return voevent.p_astro

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

    def get_likely_event_type(self, event_id: str) -> tuple:
        """
        Return the most likely event type of a certain event.

        Parameters
        ----------
        event_id : str
            The event ID you want to know the event type of.

        Returns
        -------
        tuple
            Containing the event type and the likelihood of that event.
        """
        try:
            event_types = self.events.loc[event_id, 'event_types']
            most_likely, confidence = sorted(
                event_types.items(), key=lambda value: value[1], reverse=True)[0]
        except AttributeError:
            logging.error(f"Failed to get most likely event of {event_id}")
            return None, None

        return most_likely, confidence

    def latest(self) -> pd.Series:
        """
        Return the latest event from the Grace database.

        Returns
        -------
        pandas.Series
            Latest event.
        """
        return self.events.iloc[0]

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


def mpc_to_mly(num_in_mpc: float) -> float:
    """
    Convert a number from megaparsec to million light years.

    Parameters
    ----------
    num_in_mpc : float
        Distance in megaparsec to convert.

    Returns
    -------
    float
        Distance in million light years.
    """
    return num_in_mpc * 3.2637977445371


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

    return timeago.format(dt.to_pydatetime().replace(tzinfo=pytz.UTC), current_date)

if __name__ == '__main__':
    events = Events()
    events.update_events()