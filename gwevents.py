import ligo.gracedb.rest
import pandas as pd


class Events(object):
    """
    Holds a pandas DataFrame with all super events from the Grace database.
    """

    def __init__(self):
        self.client = ligo.gracedb.rest.GraceDb()
        self.events = pd.DataFrame()
        self.update_events()

    def update_events(self):
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

    def latest(self):
        return self.events.iloc[0]

    def picture(self, event_id):
        files = self.client.files(event_id).json()
        link = files.get('bayestar.png', None)

        if link is None:
            raise FileNotFoundError
        else:
            return link

