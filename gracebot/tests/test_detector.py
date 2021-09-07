import pytest

from datetime import timedelta
from unittest import TestCase

from detector import Detector

source = "./tests/data/detector_status.html"
source2 = "./tests/data/detector_status2.html"


@pytest.fixture(scope="class")
def hanford_observing(request):
    detector = Detector("Hanford", source=source)
    request.cls.detector = detector

    yield


@pytest.mark.usefixtures("hanford_observing")
class TestHanford(TestCase):
    def test_name(self):
        assert self.detector.name == "Hanford"

    def test_status(self):
        assert self.detector.status == "Observing"

    def test_duration(self):
        assert self.detector.status_duration == timedelta(minutes=51)


@pytest.fixture(scope="class")
def livingston_down(request):
    detector = Detector("Livingston", source=source)
    request.cls.detector = detector

    yield


@pytest.mark.usefixtures("livingston_down")
class TestLivingston(TestCase):
    def test_name(self):
        assert self.detector.name == "Livingston"

    def test_status(self):
        assert self.detector.status == "Down"

    def test_duration(self):
        assert self.detector.status_duration == timedelta(minutes=2)


@pytest.fixture(scope="class")
def virgo_adjusting(request):
    detector = Detector("Virgo", source=source)
    request.cls.detector = detector

    yield


@pytest.mark.usefixtures("virgo_adjusting")
class TestVirgo(TestCase):
    def test_name(self):
        assert self.detector.name == "Virgo"

    def test_status(self):
        assert self.detector.status == "Adjusting"

    def test_duration(self):
        assert self.detector.status_duration == timedelta(minutes=10)


@pytest.fixture(scope="class")
def hanford_down(request):
    detector = Detector("Hanford", source=source2)
    request.cls.detector = detector

    yield


@pytest.mark.usefixtures("hanford_down")
class TestHanford2(TestCase):
    def test_name(self):
        assert self.detector.name == "Hanford"

    def test_status(self):
        assert self.detector.status == "Down"

    def test_duration(self):
        assert self.detector.status_duration == timedelta(hours=5, minutes=37)


@pytest.fixture(scope="class")
def livingston_not_locked(request):
    detector = Detector("Livingston", source=source2)
    request.cls.detector = detector

    yield


@pytest.mark.usefixtures("livingston_not_locked")
class TestReplacingUnderscoreInStateWithSpace(TestCase):
    def test_name(self):
        assert self.detector.name == "Livingston"

    def test_status(self):
        assert self.detector.status == "Not locked"

    def test_duration(self):
        assert self.detector.status_duration == timedelta(hours=5, minutes=37)


@pytest.fixture(scope="class")
def virgo_science(request):
    detector = Detector("Virgo", source=source2)
    request.cls.detector = detector

    yield


@pytest.mark.usefixtures("virgo_science")
class TestHoursOver24(TestCase):
    def test_name(self):
        assert self.detector.name == "Virgo"

    def test_status(self):
        assert self.detector.status == "Science"

    def test_duration(self):
        assert self.detector.status_duration == timedelta(hours=36, minutes=44)


@pytest.fixture(scope="class")
def virgo_info_too_old(request):
    detector = Detector("Virgo", source="./data/detector_status_no_time.html")
    request.cls.detector = detector

    yield


@pytest.mark.usefixtures("virgo_info_too_old")
class TestWithoutTime(TestCase):
    def test_name(self):
        assert self.detector.name == "Virgo"

    def test_status(self):
        assert self.detector.status == "Info too old"

    def test_duration(self):
        assert self.detector.status_duration == timedelta(0)
