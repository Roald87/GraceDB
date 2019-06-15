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
        assert self.voe.id == "S190521r"

    def test_p_astro(self):
        expected = {
            "BNS": 0.0,
            "NSBH": 0.0,
            "BBH": 0.9993323440548098,
            "MassGap": 0.0,
            "Terrestrial": 0.0006676559451902493,
        }

        assert self.voe.p_astro == approx(expected, abs=1e-5)
