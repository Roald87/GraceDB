import logging
import requests

from datetime import timedelta, datetime
from html.parser import HTMLParser


class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.data = []

    def handle_data(self, data):
        if data[:2] != "\n":
            self.data.append(data)


retrieve_date = datetime(1987, 4, 3)
text = ""


class Detector:
    default_source = "https://ldas-jobs.ligo.caltech.edu/~gwistat/gwistat/gwistat.html"

    def __init__(self, name, source=default_source):
        self.name = name
        self.source = source
        self.status = ""
        self.status_icon = ""
        self.status_duration = timedelta(0)
        self.__post_init__()

    @property
    def age(self):
        global retrieve_date
        return datetime.now() - retrieve_date

    def __post_init__(self):
        global retrieve_date
        global text

        if self.age < timedelta(minutes=1):
            pass
        elif self._remote_source():
            text = requests.get(self.source).text
            retrieve_date = datetime.now()
        else:
            with open(self.source, "r") as file:
                text = file.read()

        parser = MyHTMLParser()
        parser.feed(text)

        detector_index = [i for i, t in enumerate(parser.data) if self.name in t][0]

        status_raw = parser.data[detector_index + 1]
        self.status = status_raw.replace("_", " ").lower().capitalize()

        self.status_icon = self._get_status_icon()

        duration = parser.data[detector_index + 2]
        self.status_duration = self._convert_to_time(duration)

    def _get_status_icon(self) -> str:
        check_mark = ":white_check_mark:"
        cross = ":x:"
        construction = ":construction:"
        status_mapper = {
            "observing": check_mark,
            "up": check_mark,
            "science": check_mark,
            "not locked": cross,
            "down": cross,
            "info too old": cross,
            "maintenance": construction,
            "locking": construction,
            "troubleshooting": construction,
            "calibration": construction,
        }

        status_icon = status_mapper.get(self.status.lower(), ":question:")
        if status_icon == ":question:":
            logging.warning(f"Unknown status {self.status}")

        return status_icon

    def _remote_source(self) -> bool:
        return self.source.split(":")[0] == "https"

    def _convert_to_time(self, time_string: str) -> timedelta:
        try:
            hours, minutes = time_string.split(":")
            h = int(hours[1:]) if hours[0] == ">" else int(hours)
            m = int(minutes)
        except ValueError:
            logging.error(f"Could not convert the string '{time_string}' to a time.")
            h, m = 0, 0

        return timedelta(hours=h, minutes=m)
