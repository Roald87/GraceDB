import logging
from xml.etree import ElementTree

from astropy.io import fits
from ligo.gracedb.exceptions import HTTPError
from ligo.gracedb.rest import GraceDb

from config import logging_kwargs
from functions import mpc_to_mly

logging.basicConfig(**logging_kwargs)


class VOEvent(object):
    def __init__(self):
        self.client = GraceDb()
        self._xml = None
        self._skymap_url = None

    @property
    def xml(self) -> ElementTree.Element:
        return self._xml

    @property
    def distance(self):
        """
        Return distance of event in million light years.
        """
        if not self._skymap_url:
            self._get_skymap()

        with fits.open(self._skymap_url) as fit_data:
            return mpc_to_mly(fit_data[1].header["DISTMEAN"])

    @property
    def distance_std(self):
        """
        Return one sigma uncertainty in distance in million light years.
        """
        if not self._skymap_url:
            self._get_skymap()

        with fits.open(self._skymap_url) as fit_data:
            return mpc_to_mly(fit_data[1].header["DISTSTD"])

    @property
    def id(self) -> str:
        """
        Return event id.
        """
        assert self._xml, "Load an xml file first using from_file or from_event_id!"

        for child in self._xml.findall("What/"):
            if child.get("name") == "GraceID":
                return child.get("value")

    @property
    def p_astro(self) -> dict:
        p_astro = dict().fromkeys(["BNS", "NSBH", "BBH", "MassGap", "Terrestrial"], 0.0)

        for child in self._xml.findall("What/Group/"):
            name = child.get("name")
            if name in p_astro:
                p_astro[name] = float(child.get("value"))

        return p_astro

    def _get_skymap(self):
        assert self._xml, "Load an xml file first using from_file or from_event_id!"

        for child in self._xml.findall(".//Param"):
            if child.get("name") == "skymap_fits":
                self._skymap_url = child.get("value")
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
        voevents = self.client.voevents(event_id).json()["voevents"]
        voevents.sort(key=lambda x: x["N"], reverse=True)

        # For event S190517h the file 'S190517h-3-Initial.xml' was in the
        # voevent filelist. However, this file doesn't exist. Therefore looping
        # over all until a existing file is found.
        for voevent in voevents:
            url = voevent["links"]["file"]
            try:
                voevent_xml = self.client.get(url)
                self._xml = ElementTree.parse(voevent_xml).getroot()
                break
            except HTTPError:
                if voevent["N"] == 1:
                    logging.error(f"Can't find VOEvent for event {event_id}")
                    raise HTTPError
                else:
                    logging.warning(f"Failed to get voevent from {url}")

    def from_string(self, string: str):
        self._xml = ElementTree.ElementTree(ElementTree.fromstring(string)).getroot()


if __name__ == "__main__":
    # For testing purposes
    event = VOEvent()
    # event.from_file('MS181101ab-1-Preliminary.xml')
    # event.from_file('MS181101ab-3-Update.xml')
    event.from_event_id("S190521r")

    print(event.distance)
    print(event.distance_std)
