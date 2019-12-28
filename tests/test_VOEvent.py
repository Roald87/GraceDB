from unittest import TestCase
from unittest.mock import Mock, patch, MagicMock

import pytest
from pytest import approx

from functions import mpc_to_mly
from voevent import VOEventFromXml, VOEventFromEventId
import tests.voevent_test_data as test_data
from ligo.gracedb.exceptions import HTTPError


@patch("ligo.gracedb.rest.GraceDb.voevents")
def test_getting_event_from_event_id(mock_get):
    mock_get.return_value = Mock(ok=True)
    expected_event_json = test_data.expected_event_json
    mock_get.return_value.json.return_value = expected_event_json

    voevent = VOEventFromEventId()
    actual_event_json = voevent._get_voevents_json("S190521r")

    assert actual_event_json == expected_event_json["voevents"]


def test_sort_voevent_newest_should_be_first():
    voevent = VOEventFromEventId()
    unsorted_json = test_data.unsorted_json_S190521r
    actual_json = voevent._sort_voevents_newest_first(unsorted_json)

    assert actual_json == test_data.sorted_json_S190521r


@patch("ligo.gracedb.rest.GraceDb.get")
def test_get_latest_voevent(mock_get):
    mock_get.return_value = Mock(ok=True)
    mock_get.side_effect = load_data_S190521r

    voevent = VOEventFromEventId()
    result = voevent._try_get_latest_voevent(test_data.sorted_json_S190521r)

    expected = test_data.read_xml("./data/S190521r-2-Initial.xml")

    assert result == expected


def load_data_S190521r(event_url):
    return test_data.voevents_S190521r[event_url]


@patch("ligo.gracedb.rest.GraceDb.get")
def test_get_latest_voevent_should_raise_http_error_on_latest_voevent_and_get_older_one(
    mock_get
):
    mock_get.return_value = Mock(ok=True)
    mock_get.side_effect = (
        HTTPError(status=400, reason="Bad Request", message="Bad Request"),
        test_data.read_xml("./data/S190517h-2-Initial.xml"),
    )

    voevent = VOEventFromEventId()
    result = voevent._try_get_latest_voevent(test_data.sorted_json_S190517h)

    expected = test_data.read_xml("./data/S190517h-2-Initial.xml")

    assert result == expected


@pytest.fixture(scope="class")
def event_id(request):
    voe = VOEventFromEventId()
    voe.get("S190521r")

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
    voe = VOEventFromXml()
    voe.get("./data/MS181101ab-1-Preliminary.xml")

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
    voe = VOEventFromXml()
    voe.get("./data/S190701ah-3-Update.xml")

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
