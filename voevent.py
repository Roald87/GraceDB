import logging
from xml.etree import ElementTree

from astropy.io import fits
from ligo.gracedb.rest import GraceDb

from config import logging_kwargs
from functions import mpc_to_mly

logging.basicConfig(**logging_kwargs)


class VOEvent(object):

    def __init__(self):
        self._client = GraceDb()
        self._xml = None
        self._skymap_url = None

    @property
    def xml(self) -> ElementTree.Element:
        return self._xml

    @property
    def distance(self):
        if not self._skymap_url:
            self._get_skymap()

        with fits.open(self._skymap_url) as fit_data:
            return mpc_to_mly(fit_data[1].header['DISTMEAN'])

    @property
    def distance_std(self):
        if not self._skymap_url:
            self._get_skymap()

        with fits.open(self._skymap_url) as fit_data:
            return mpc_to_mly(fit_data[1].header['DISTSTD'])

    @property
    def id(self) -> str:
        assert self._xml, "Load an xml file first using from_file or from_event_id!"

        for _child in self._xml.findall('What/'):
            if _child.get('name') == 'GraceID':
                return _child.get('value')

    @property
    def p_astro(self) -> dict:
        _p_astro = dict().fromkeys(
            ['BNS', 'NSBH', 'BBH', 'MassGap', 'Terrestrial'], 0.0)

        for _child in self._xml.findall('What/Group/'):
            _name = _child.get('name')
            if _name in _p_astro:
                _p_astro[_name] = float(_child.get('value'))

        return _p_astro

    def _get_skymap(self):
        assert self._xml, "Load an xml file first using from_file or from_event_id!"

        for _child in self._xml.findall('.//Param'):
             if _child.get('name') == 'skymap_fits':
                self._skymap_url = _child.get('value')
                break
        else:
            raise FileNotFoundError("Couldn't find a skymap URL.")

    def from_file(self, filename: str):
        self._xml = ElementTree.parse(filename).getroot()

    def from_event_id(self, event_id: str):
        """
        Get the most recent VOEvent of this event.

        Data is taken directly from the GraceDB.

        Parameters
        ----------
        event_id : str

        Returns
        -------
        None
        """
        all_event_files = self._client.files(event_id).json()

        voevent_filter =  lambda x: (event_id in x) and (x[-4:] == '.xml')
        voevents = list(filter(voevent_filter, all_event_files))

        sort_key = lambda x: int(x.split('-')[1])
        most_recent_voevent = sorted(voevents, key=sort_key, reverse=True)[0]

        voevent_xml = self._client.get(all_event_files[most_recent_voevent])
        self._xml = ElementTree.parse(voevent_xml).getroot()

    def from_string(self, string: str):
        self._xml = ElementTree.ElementTree(ElementTree.fromstring(string)).getroot()


if __name__ == "__main__":
    event = VOEvent()
    # event.from_file('MS181101ab-1-Preliminary.xml')
    # event.from_file('MS181101ab-3-Update.xml')
    event.from_event_id('S190521r')

    print(event.distance)
    print(event.distance_std)