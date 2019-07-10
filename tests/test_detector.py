from datetime import time
from unittest import TestCase

from detector import Detector

source = "./data/detector_status.html"
source2 = "./data/detector_status2.html"


class TestHanford(TestCase):
    def setUp(self):
        self.hanford = Detector("Hanford", source=source)

    def test_name(self):
        assert self.hanford.name == "Hanford"

    def test_status(self):
        assert self.hanford.status == "Observing"

    def test_duration(self):
        assert self.hanford.duration == time(0, 51)


class TestLivingston(TestCase):
    def setUp(self):
        self.livingston = Detector("Livingston", source=source)

    def test_name(self):
        assert self.livingston.name == "Livingston"

    def test_status(self):
        assert self.livingston.status == "Down"

    def test_duration(self):
        assert self.livingston.duration == time(0, 2)


class TestVirgo(TestCase):
    def setUp(self):
        self.virgo = Detector("Virgo", source=source)

    def test_name(self):
        assert self.virgo.name == "Virgo"

    def test_status(self):
        assert self.virgo.status == "Adjusting"

    def test_duration(self):
        assert self.virgo.duration == time(0, 10)


class TestHanford2(TestCase):
    def setUp(self):
        self.hanford = Detector("Hanford", source=source2)

    def test_name(self):
        assert self.hanford.name == "Hanford"

    def test_status(self):
        assert self.hanford.status == "Down"

    def test_duration(self):
        assert self.hanford.duration == time(5, 37)


class TestReplacingUnderscoreInStateWithSpace(TestCase):
    def setUp(self):
        self.detector = Detector("Livingston", source=source2)

    def test_name(self):
        assert self.detector.name == "Livingston"

    def test_status(self):
        assert self.detector.status == "Not locked"

    def test_duration(self):
        assert self.detector.duration == time(5, 37)


class TestWithoutTime(TestCase):
    def setUp(self):
        self.detector = Detector("Virgo", source="./data/detector_status_no_time.html")

    def test_name(self):
        assert self.detector.name == "Virgo"

    def test_status(self):
        assert self.detector.status == "Info too old"

    def test_duration(self):
        assert self.detector.duration == time(0)
