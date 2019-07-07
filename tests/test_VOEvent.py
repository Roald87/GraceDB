from unittest import TestCase

from pytest import approx

from functions import mpc_to_mly
from voevent import VOEvent


class TestFromEventId(TestCase):
    def setUp(self) -> None:
        self.voe = VOEvent()
        event_id = "S190521r"
        self.voe.from_event_id(event_id)

    def test_distance(self):
        assert self.voe.distance == approx(mpc_to_mly(1136.13018), abs=1e-4)

    def test_distance_std(self):
        assert self.voe.distance_std == approx(mpc_to_mly(279.257795), abs=1e-4)

    def test_id(self):
        assert self.voe.id.lower() == "s190521r"

    def test_p_astro(self):
        expected = {
            "BNS": 0.0,
            "NSBH": 0.0,
            "BBH": 0.9993323440548098,
            "MassGap": 0.0,
            "Terrestrial": 0.0006676559451902493,
        }

        assert self.voe.p_astro == approx(expected, abs=1e-5)


class TestFromMockDataFile(TestCase):
    def setUp(self) -> None:
        self.voe = VOEvent()
        self.voe.from_file("./data/MS181101ab-1-Preliminary.xml")

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


class TestFromRealEventFile(TestCase):
    def setUp(self) -> None:
        self.voe = VOEvent()
        self.voe.from_file("./data/S190701ah-3-Update.xml")

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
