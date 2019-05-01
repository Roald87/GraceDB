import ligo.gracedb.rest
import pandas as pd
from astropy.io import fits

from image import ImageFromUrl


class Events(object):
    """
    Holds a pandas DataFrame with all super events from the Grace database.
    """

    def __init__(self):
        self.client = ligo.gracedb.rest.GraceDb()
        self.events = pd.DataFrame()
        self.update_events()

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
        events = self.client.superevents(query='Production', orderby=['-created'])

        df = pd.DataFrame()
        for event in events:
            event.pop('links')
            labels = event.pop('labels')
            # ADVNO = advocate says event is not ok.
            if 'ADVNO' not in labels:
                df = df.append({**event, 'labels': [labels]}, ignore_index=True)
        df.set_index('superevent_id', inplace=True)
        df['created'] = pd.to_datetime(df['created'])

        self.events = df

        self._add_possible_event_types()
        self._add_event_distances()

    def _add_event_distances(self):
        """
        Adds the event distances to the event dataframe.

        Returns
        -------
        None
        """
        self.events = self.events.reindex(
            columns=list(self.events) +['distance_mean_Mly', 'distance_std_Mly'])

        for event_name, _ in self.events.iterrows():
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


    def _add_possible_event_types(self):
        """
        Adds the event type to the events dataframe.

        Possible event types are binary black hole merger, black hole neutron
        star merger etc.

        Returns
        -------
        None
        """

        _all_types = pd.Series(name='event_types')
        for event_name, _ in self.events.iterrows():
            try:
                event_type = self.client.files(event_name, 'p_astro.json').json()
            except ligo.gracedb.exceptions.HTTPError:
                pass
            _all_types[event_name] = event_type

        self.events = pd.concat([self.events, _all_types], axis=1)

    def get_event_type(self, event_id: str) -> str:
        """

        Returns
        -------

        """
        _event_types = {
            # Probability that the source is a binary black hole merger (both
            # objects heavier than 5 solar masses)
            'BBH': 'binary black hole merger',
            # Probability that the source is a binary neutron star merger
            # (both objects lighter than 3 solar masses)
            'BNS': 'binary neutron star merger',
            # Probability that the source is a neutron star-black hole merger
            # (primary heavier than 5 solar masses, secondary lighter than 3
            # solar masses)
            'NSBH': 'neutron start black hole merger',
            # Probability that the source is terrestrial(i.e., a background
            # noise fluctuation or a glitch)
            'Terrestrial': 'terrestrial',
            # Probability that the source has at least one object between 3 and
            # 5 solar masses
            'MassGap': 'mass gap',
        }

        event_types = self.events.loc[event_id, 'event_types']
        most_likely, confidence = sorted(
            event_types.items(), key=lambda value: value[1], reverse=True)[0]

        return _event_types[most_likely], confidence

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
            Local path of the cropped image.
        """
        files = self.client.files(event_id).json()
        link = get_latest_file_url(files, 'bayestar', '.png')

        if link is None:
            raise FileNotFoundError
        else:
            img = ImageFromUrl(link)
            img_fname = img.reduce_whitespace()

        return img_fname


def get_latest_file_url(files: dict, starts_with: str, ends_with: str) -> str:
    """
    Get the url to a file which should start and end with a specific string.

    Parameters
    ----------
    files : dict
        Keys are the filenames and the values are the urls.
    starts_with : str
        Start of the filename.
    ends_with : str
        End of the filename, usually the extension of the file.

    Returns
    -------
    str
        url of the most recent file.
    """
    filtered_files = {fname: link for fname, link in files.items()
                      if (starts_with in fname[:len(starts_with)])
                      and fname[-len(ends_with):] == ends_with
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
