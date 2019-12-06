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
        self.distance = 0
        self.distance_std = 0

    @property
    def id(self) -> str:
        """
        Return event id.
        """
        return self._data["GraceID"]

    @property
    def seen_by_short(self) -> list:
        """
        Return abbreviated names of the instruments which measured the event.
        """
        return self._data["Instruments"].split(",")

    @property
    def seen_by_long(self) -> list:
        """
        Return full names of the instruments which measured the event.
        """
        name_map = {"V1": "Virgo", "L1": "Livingston", "H1": "Hanford"}

        return [name_map.get(name, "") for name in self.seen_by_short]

    @property
    def p_astro(self) -> Dict[str, float]:
        p_astro = dict().fromkeys(  # type: ignore
            ["BNS", "NSBH", "BBH", "MassGap", "Terrestrial"], 0.0
        )

        for key in p_astro.keys():
            try:
                p_astro[key] = float(self._data[key])
            except KeyError:
                logging.warning(f"Couldn't find {key} in VOEvent xml!")
                pass

        return p_astro

    def _add_distance(self, url: str):
        try:
            with fits.open(url) as fit_data:
                self.distance = mpc_to_mly(fit_data[1].header["DISTMEAN"])
                self.distance_std = mpc_to_mly(fit_data[1].header["DISTSTD"])
        except KeyError as e:
            logging.warning(
                f"Couldn't get the distance from event url {url}.\n" + f"Exception: {e}"
            )
            pass

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
