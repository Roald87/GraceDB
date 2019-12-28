from unittest import TestCase

import pytest
from pytest import approx

from functions import mpc_to_mly
from voevent import VOEventFromXml, VOEventFromEventId


@pytest.fixture(scope="class")
def event_id(request):
    voe = VOEventFromEventId("S190521r")
    request.cls.voe = voe

    yield


@pytest.mark.usefixtures("event_id")
class TestFromEventId(TestCase):
    def test_distance(self):
        assert self.voe.distance == approx(mpc_to_mly(1136.13018), abs=1e-4)

    def test_distance_std(self):
        assert self.voe.distance_std == approx(mpc_to_mly(279.257795), abs=1e-4)

    def test_id(self):
        assert self.voe.id.lower() == "s190521r"

    def test_short_names(self):
        assert self.voe.seen_by_short == ["H1", "L1"]

    def test_long_names(self):
        assert self.voe.seen_by_long == ["Hanford", "Livingston"]

    def test_p_astro(self):
        expected = {
            "BNS": 0.0,
            "NSBH": 0.0,
            "BBH": 0.9993323440548098,
            "MassGap": 0.0,
            "Terrestrial": 0.0006676559451902493,
        }

        assert self.voe.p_astro == approx(expected, abs=1e-5)


@pytest.fixture(scope="class")
def mock_event_file(request):
    voe = VOEventFromXml("./data/MS181101ab-1-Preliminary.xml")
    request.cls.voe = voe

    yield


@pytest.mark.usefixtures("mock_event_file")
class EventFromMockEvent(TestCase):
    def test_distance(self):
        assert self.voe.distance == approx(mpc_to_mly(39.7699960), abs=1e-4)

    def test_distance_std(self):
        assert self.voe.distance_std == approx(mpc_to_mly(8.30843505), abs=1e-4)

    def test_id(self):
        assert self.voe.id.lower() == "s190602aq"

    def test_p_astro(self):
        expected = {
            "BNS": 0.95,
            "NSBH": 0.01,
            "BBH": 0.03,
            "MassGap": 0.0,
            "Terrestrial": 0.01,
        }

        assert self.voe.p_astro == approx(expected, abs=1e-5)


@pytest.fixture(scope="class")
def real_event_file(request):
    voe = VOEventFromXml("./data/S190701ah-3-Update.xml")
    request.cls.voe = voe

    yield


@pytest.mark.usefixtures("real_event_file")
class TestFromRealEventFile(TestCase):
    def test_distance(self):
        assert self.voe.distance == approx(mpc_to_mly(1848.9383223), abs=1e-4)

    def test_distance_std(self):
        assert self.voe.distance_std == approx(mpc_to_mly(445.5334849617994), abs=1e-4)

    def test_id(self):
        assert self.voe.id.lower() == "s190701ah"

    def test_p_astro(self):
        expected = {
            "BNS": 0.0,
            "NSBH": 0.0,
            "BBH": 0.9343726,
            "MassGap": 0.0,
            "Terrestrial": 0.0656274,
        }

        assert self.voe.p_astro == approx(expected, abs=1e-5)
