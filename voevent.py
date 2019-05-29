import logging
from xml.etree import ElementTree

from ligo.gracedb.rest import GraceDb

from config import logging_kwargs

logging.basicConfig(**logging_kwargs)

class VOEvent(object):

    def __init__(self):
        self.client = GraceDb()
        self._xml = None

    @property
    def xml(self):
        return self._xml

    def from_file(self, filename):
        self._xml = ElementTree.parse(filename).getroot()


    def from_event_id(self, event_id: str):
        """
        Return the most recent VOEvent of this event.

        Gets the data directly from the GraceDB.

        Parameters
        ----------
        event_id : str

        Returns
        -------

        """
        logging.info(f"Fetching event files of {event_id}.")
        all_event_files = self.client.files(event_id).json()

        voevent_filter =  lambda x: (event_id in x) and (x[-4:] == '.xml')
        voevents = list(filter(voevent_filter, all_event_files))

        sort_key = lambda x: int(x.split('-')[1])
        most_recent_voevent = sorted(voevents, key=sort_key, reverse=True)[0]

        logging.info(f"Fetching {most_recent_voevent}.")
        voevent_xml = self.client.get(all_event_files[most_recent_voevent])
        self._xml = ElementTree.parse(voevent_xml).getroot()


if __name__ == "__main__":
    event = VOEvent()
    # event.from_file('MS181101ab-1-Preliminary.xml')
    event.from_event_id('S190524q')

    for child in event.xml.findall('What/'):
        print(child.get('name'))