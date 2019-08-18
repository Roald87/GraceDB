import os

import pytest

from permanentset import PermanentSet


@pytest.fixture(scope="session", autouse=True)
def int_set():
    # Run before tests are started
    test_filename = "int_test.txt"
    p_int_set = PermanentSet(test_filename, int)
    yield p_int_set

    # Run after tests have finished
    os.remove(test_filename)


def test_add_int(int_set):
    int_set.add(34)
    assert len(int_set.data) == 1
    assert int_set.data == {34}


def test_add_second_int(int_set):
    int_set.add(123)
    assert len(int_set.data) == 2
    assert int_set.data == {34, 123}


def test_load_old_data_int(int_set):
    test_filename = "int_test.txt"
    p_int_set = PermanentSet(test_filename, int)
    assert len(p_int_set.data) == 2
    assert p_int_set.data == {34, 123}


def test_add_third_int(int_set):
    int_set.add(29)
    assert len(int_set.data) == 3
    assert int_set.data == {34, 123, 29}


def test_remove_second_int(int_set):
    int_set.remove(123)
    assert len(int_set.data) == 2
    assert int_set.data == {34, 29}


def test_remove_non_existing_item(int_set):
    int_set.remove(7)
    assert len(int_set.data) == 2
    assert int_set.data == {34, 29}


@pytest.fixture(scope="session", autouse=True)
def string_set():
    # Run before tests are started
    test_filename = "string_test.txt"
    p_string_set = PermanentSet(test_filename, str)
    yield p_string_set

    # Run after tests have finished
    os.remove(test_filename)


def test_add_first_string(string_set):
    string_set.add("foo")
    assert len(string_set.data) == 1
    assert string_set.data == {"foo"}


def test_add_second_string(string_set):
    string_set.add("bar")
    assert len(string_set.data) == 2
    assert string_set.data == {"foo", "bar"}


def test_load_old_string_data(string_set):
    test_filename = "string_test.txt"
    loaded_string_set = PermanentSet(test_filename, str)
    assert len(loaded_string_set.data) == 2
    assert loaded_string_set.data == {"foo", "bar"}


def test_add_third_string(string_set):
    string_set.add("1234")
    assert len(string_set.data) == 3
    assert string_set.data == {"foo", "bar", "1234"}
