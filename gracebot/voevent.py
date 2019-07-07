import logging
from typing import Dict
from xml.etree import ElementTree

from astropy.io import fits
from ligo.gracedb.exceptions import HTTPError
from ligo.gracedb.rest import GraceDb

from config import logging_kwargs
from functions import mpc_to_mly

logging.basicConfig(**logging_kwargs)  # type: ignore


class VOEvent(object):
    def __init__(self):
        self.client = GraceDb()
        self._data = {}
        self._distance = 0
        self._distance_std = 0

    @property
    def distance(self) -> float:
        """
        Return distance of event in million light years.
        """
        return self._distance

    @property
    def distance_std(self) -> float:
        """
        Return one sigma uncertainty in distance in million light years.
        """
        return self._distance_std

    @property
    def id(self) -> str:
        """
        Return event id.
        """
        return self._data["GraceID"]

    @property
    def p_astro(self) -> Dict[str, float]:
        p_astro = dict().fromkeys(  # type: ignore
            ["BNS", "NSBH", "BBH", "MassGap", "Terrestrial"], 0.0
        )

        for key in p_astro.keys():
            try:
                p_astro[key] = float(self._data[key])
            except KeyError:
                logging.warning(f"Couldn't find {key} in VOEent xml!")
                pass

        return p_astro

    def _add_distance(self, url: str):
        with fits.open(url) as fit_data:
            self._distance = mpc_to_mly(fit_data[1].header["DISTMEAN"])
            self._distance_std = mpc_to_mly(fit_data[1].header["DISTSTD"])

    def _xml_to_dict(self, root: ElementTree.Element) -> Dict[str, str]:
        return {
            elem.attrib["name"]: elem.attrib["value"]
            for elem in root.iterfind(".//Param")
        }

    def from_file(self, filename: str) -> None:
        root = ElementTree.parse(filename).getroot()
        self._data = self._xml_to_dict(root)
        self._add_distance(self._data["skymap_fits"])

    def from_event_id(self, event_id: str) -> None:
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
        # voevent file list. However, this file doesn't exist. Therefore looping
        # over all until a existing file is found.
        for voevent in voevents:
            url = voevent["links"]["file"]
            try:
                xml = self.client.get(url)
                root = ElementTree.parse(xml).getroot()
                self._data = self._xml_to_dict(root)
                break
            except HTTPError:
                if voevent["N"] == 1:
                    logging.error(f"Can't find VOEvent for event {event_id}")
                    raise HTTPError
                else:
                    logging.warning(f"Failed to get voevent from {url}")
        self._add_distance(self._data["skymap_fits"])


if __name__ == "__main__":
    # For testing purposes
    event = VOEvent()
    # event.from_file('MS181101ab-1-Preliminary.xml')
    # event.from_file('MS181101ab-3-Update.xml')
    event.from_event_id("S190521r")

    print(event.distance)
    print(event.distance_std)
    print(event.id)
    print(event.p_astro)
