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
        link = files.get('bayestar.png', None)

        if link is None:
            raise FileNotFoundError
        else:
            img = ImageFromUrl(link)
            img_fname = img.reduce_whitespace()

        return img_fname

