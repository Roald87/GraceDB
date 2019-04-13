import ligo.gracedb.rest
import pandas as pd


class Events(object):
    """
    Holds a pandas DataFrame with all super events from the Grace database.
    """

    def __init__(self):
        self.events = pd.DataFrame()
        self.update_events()

    def update_events(self):
        client = ligo.gracedb.rest.GraceDb()
        events = client.superevents(query='Production', orderby=['-created'])

        df = pd.DataFrame()
        for event in events:
            links = event.pop('links')
            labels = event.pop('labels')
            # ADVNO = advocate says event is not ok.
            if 'ADVNO' not in labels:
                df = df.append({**event, 'labels': [labels]}, ignore_index=True)
        df.set_index('superevent_id', inplace=True)
        df['created'] = pd.to_datetime(df['created'])

        self.events = df

    def latest(self):

        return self.events.iloc[0]







# def _update_events():
#     client = GraceDb()
#     events = client.superevents(query='Production', orderby=['created'])
#
#     df = pd.DataFrame()
#     for event in events:
#         # links = event.pop('links')
#         labels = event.pop('labels')
#         # ADVNO = advocate says event is not ok.
#         if 'ADVNO' not in labels:
#             df = df.append({**event, 'labels': [labels]}, ignore_index=True)
#     df.set_index('superevent_id', inplace=True)
#     df['created'] = pd.to_datetime(df['created'])
#
#     return events
#
# def latest(events):
#
#     last_event = next(events)
#     name = last_event['superevent_id']
#     date = last_event['created']
#     # category = last_event['category']
#
#     event_info = f'The last event was {name} at {date}'
#
#     return event_info
#
# events = _update_events()
#
#
#
# timeago.format(df['created'][0].to_pydatetime(), datetime.datetime.now(datetime.timezone.utc))
#
# print(df)

