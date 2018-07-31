import pytest

import fastpac.picker as picker

def test_picker_random(monkeypatch):
    # Result of the mock random function
    random_var = 0
    # Length that should be passed in
    length_var = 0

    def mockrandom(num, length):
        assert length == length_var
        return random_var

    monkeypatch.setattr(picker, "randrange", mockrandom)

    random_var = 1
    length_var = 3
    mirrorpicker = picker.RandomPicker(["a", "b", "c"])
    assert mirrorpicker.next() == "b"

    random_var = 0
    length_var = 2
    mirrorpicker = picker.RandomPicker(["a", "b"])
    assert mirrorpicker.next() == "a"

    random_var = 0
    length_var = 1
    mirrorpicker = picker.RandomPicker(["a"])
    assert mirrorpicker.next() == "a"

    # get_mirrors
    mirrorpicker = picker.RandomPicker(["a", "b"])
    assert mirrorpicker.get_mirrors() == ["a", "b"]

    # With removed mirror
    random_var = 0
    length_var = 1
    mirrorpicker = picker.RandomPicker(["a", "b"])
    mirrorpicker.remove("a")
    assert mirrorpicker.get_mirrors() == ["b"]

def test_picker_datacap():
    # size of one mb in bytes
    mb = 10**6

    mirrorpicker = picker.CapPicker(["a", "b", "c"], arg=5*mb)
    assert mirrorpicker.next(size=6*mb) == "a"
    assert mirrorpicker.get_mirrors() == ["b", "c"]

    assert mirrorpicker.next(size=3*mb) == "b"
    assert mirrorpicker.next(size=3*mb) == "c"
    assert mirrorpicker.get_mirrors() == ["b", "c"]

    mirrorpicker = picker.CapPicker(["a", "b", "c"], 5*mb)
    assert mirrorpicker.next(size=2*mb) == "a"
    assert mirrorpicker.next(size=2*mb) == "a"
    assert mirrorpicker.get_mirrors() == ["a", "b", "c"]

def test_picker_counter():

    mirrorpicker = picker.CounterPicker(["a", "b", "c"], arg=1)
    assert mirrorpicker.next() == "a"
    assert mirrorpicker.next() == "b"
    assert mirrorpicker.next() == "c"
    assert mirrorpicker.next() == "a"
    assert mirrorpicker.next() == "b"
    assert mirrorpicker.next() == "c"

    mirrorpicker = picker.CounterPicker(["a", "b", "c"], arg=2)
    assert mirrorpicker.next() == "a"
    assert mirrorpicker.next() == "a"
    assert mirrorpicker.next() == "b"
    assert mirrorpicker.next() == "b"
    assert mirrorpicker.next() == "c"
    assert mirrorpicker.next() == "c"
    assert mirrorpicker.next() == "a"

def test_picker_single():

    mirrorpicker = picker.SinglePicker(["a", "b", "c"])
    assert mirrorpicker.next() == "a"
    assert mirrorpicker.next() == "a"

def test_picker_leastused():

    mirrorpicker = picker.LeastUsedPicker(["a", "b", "c"])
    assert mirrorpicker.next(size=3) == "a"
    assert mirrorpicker.next(size=1) == "b"
    assert mirrorpicker.next(size=2) == "c"
    assert mirrorpicker.next(size=3) == "b"
    assert mirrorpicker.next(size=1) == "c"
