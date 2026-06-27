from lmx.musicxml.time.ActualDuration import ActualDuration
from lmx.musicxml.time.MeasureOnset import MeasureOnset
import pytest


def test_it_must_be_non_negative():
    with pytest.raises(ValueError):
        MeasureOnset(ActualDuration(-2, 1))

def test_it_has_value_equality():
    a = MeasureOnset(ActualDuration(2, 1))
    b = MeasureOnset(ActualDuration(4, 1))
    c = MeasureOnset(ActualDuration(2, 1))
    assert a == a
    assert a != b
    assert a == c
    assert c != b


def test_it_can_be_compared():
    a = MeasureOnset(ActualDuration(2, 1))
    b = MeasureOnset(ActualDuration(4, 1))
    assert a < b
    assert a <= b
    assert a <= a
    assert b > a
    assert b >= a
    assert a >= a


def test_duration_may_be_added_to_onset():
    onset = MeasureOnset(ActualDuration(2, 1))
    duration = ActualDuration(4, 1)
    assert (onset + duration) == MeasureOnset(ActualDuration(6, 1))
    assert (duration + onset) == MeasureOnset(ActualDuration(6, 1))

    onset += duration
    assert onset == MeasureOnset(ActualDuration(6, 1))


def test_two_onsets_may_not_be_added():
    a = MeasureOnset(ActualDuration(2, 1))
    b = MeasureOnset(ActualDuration(4, 1))
    
    with pytest.raises(TypeError):
        a + b


def test_two_onsets_may_be_subtracted():
    a = MeasureOnset(ActualDuration(2, 1))
    b = MeasureOnset(ActualDuration(4, 1))

    assert (b - a) == ActualDuration(2, 1)
    assert (a - b) == ActualDuration(-2, 1)


def test_it_doesnt_support_int_operands():
    a = MeasureOnset(ActualDuration(2, 1))

    with pytest.raises(TypeError):
        a + 5
    
    with pytest.raises(TypeError):
        a - 5

    with pytest.raises(TypeError):
        a > 5

    with pytest.raises(TypeError):
        a < 5

    with pytest.raises(TypeError):
        a >= 5
    
    with pytest.raises(TypeError):
        a <= 5


def test_it_may_be_compared_to_zero():
    zero = MeasureOnset(ActualDuration(0, 1))
    assert zero == 0
    assert zero >= 0
    assert zero <= 0
    assert 0 == zero
    assert 0 >= zero
    assert 0 <= zero
    
    one = MeasureOnset(ActualDuration(1, 1))
    assert one != 0
    assert one > 0
    assert one >= 0
    assert 0 != one
    assert 0 < one
    assert 0 <= one
