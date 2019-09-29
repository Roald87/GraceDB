from gracebot import inline_list


def test_single_name():
    result = inline_list(["l"])
    assert result == "l"


def test_multiple_names():
    result = inline_list(list("li"))
    assert result == "l and i"

    result = inline_list(list("lig"))
    assert result == "l, i and g"

    result = inline_list(list("ligo"))
    assert result == "l, i, g and o"


def test_empty_list():
    result = inline_list([])
    assert result == ""
