from dataclasses import dataclass
from datetime import time
from html.parser import HTMLParser

import requests


class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.data = []

    def handle_data(self, data):
        if data[:2] != "\n":
            self.data.append(data)


@dataclass
class Detector:

    name: str
    source: str = "https://ldas-jobs.ligo.caltech.edu/~gwistat/gwistat/gwistat.html"
    status: str = ""
    status_icon: str = ""
    duration: time = time(0)

    def __post_init__(self):
        if self._remote_source():
            text = requests.get(self.source).text
        else:
            with open(self.source, "r") as file:
                text = file.read()

        parser = MyHTMLParser()
        parser.feed(text)

        detector_index = [i for i, t in enumerate(parser.data) if self.name in t][0]

        self.status = parser.data[detector_index + 1]

        self.status_icon = self._get_status_icon()

        duration = parser.data[detector_index + 2]
        self.duration = self._convert_to_time(duration)

    def _get_status_icon(self) -> str:
        check_mark = ":white_check_mark:"
        cross = ":x:"
        construction = ":construction:"
        status_mapper = {
            "observing": check_mark,
            "up": check_mark,
            "science": check_mark,
            "not_locked": check_mark,
            "down": cross,
            "maintenance": construction,
            "locking": construction,
            "troubleshooting": construction,
        }

        return status_mapper.get(self.status.lower(), ":question:")

    def _remote_source(self) -> bool:
        return self.source.split(":")[0] == "https"

    def _convert_to_time(self, time_string: str) -> time:
        hours, minutes = time_string.split(":")
        h = int(hours[1:]) if hours[0] == ">" else int(hours)
        m = int(minutes)

        return time(h, m)
