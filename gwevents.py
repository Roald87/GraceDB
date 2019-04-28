import ligo.gracedb.rest
import pandas as pd

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
        bayestar = {fname: link for fname, link in files.items()
                    if ('bayestar' in fname)
                    and fname[-4:] == '.png'
                    and 'volume' not in fname}
        latest_bayestar = sorted(bayestar.keys())[-1]
        link = files.get(latest_bayestar, None)

        if link is None:
            raise FileNotFoundError
        else:
            img = ImageFromUrl(link)
            img_fname = img.reduce_whitespace()

        return img_fname