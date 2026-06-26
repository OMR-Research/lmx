from lmx.musicxml.time.ActualDuration import ActualDuration
from lmx.musicxml.time.MeasureOnset import MeasureOnset
from lmx.musicxml.time.PartOnset import PartOnset
import pytest


def test_it_must_be_non_negative():
    with pytest.raises(ValueError):
        PartOnset(-5, MeasureOnset(ActualDuration(2, 1)))


def test_it_has_value_equality():
    a = PartOnset(0, MeasureOnset(ActualDuration(2, 1)))
    b = PartOnset(0, MeasureOnset(ActualDuration(4, 1)))
    c = PartOnset(0, MeasureOnset(ActualDuration(2, 1)))
    assert a == a
    assert a != b
    assert a == c
    assert c != b


def test_it_can_be_compared():
    a = PartOnset(0, MeasureOnset(ActualDuration(2, 1)))
    b = PartOnset(0, MeasureOnset(ActualDuration(4, 1)))
    assert a < b
    assert a <= b
    assert a <= a
    assert b > a
    assert b >= a
    assert a >= a
    
    c = PartOnset(1, MeasureOnset(ActualDuration(2, 1)))
    assert c > a
    assert c > b


def test_duration_may_be_added_to_onset():
    onset = PartOnset(0, MeasureOnset(ActualDuration(2, 1)))
    duration = ActualDuration(4, 1)
    assert (onset + duration) == PartOnset(0, MeasureOnset(ActualDuration(6, 1)))
    assert (duration + onset) == PartOnset(0, MeasureOnset(ActualDuration(6, 1)))

def test_measure_index_may_be_advanced():
    onset = PartOnset(5, MeasureOnset(ActualDuration(2, 1)))

    # note the measure_onset is reset to zero
    assert onset.next_measure() == PartOnset(6, MeasureOnset(ActualDuration(0, 1)))


def test_two_onsets_may_not_be_added():
    a = PartOnset(5, MeasureOnset(ActualDuration(2, 1)))
    b = PartOnset(5, MeasureOnset(ActualDuration(4, 1)))
    c = MeasureOnset(ActualDuration(4, 1))
    
    with pytest.raises(TypeError):
        a + b
    
    with pytest.raises(TypeError):
        a + c


def test_two_onsets_may_be_subtracted():
    a = PartOnset(5, MeasureOnset(ActualDuration(2, 1)))
    b = PartOnset(5, MeasureOnset(ActualDuration(4, 1)))

    assert (b - a) == ActualDuration(2, 1)
    assert (a - b) == ActualDuration(-2, 1)


def test_two_onsets_may_not_be_subtracted_when_different_measure():
    a = PartOnset(5, MeasureOnset(ActualDuration(2, 1)))
    b = PartOnset(6, MeasureOnset(ActualDuration(4, 1)))
    
    with pytest.raises(ArithmeticError):
        a - b


def test_it_doesnt_support_int_operands():
    a = PartOnset(5, MeasureOnset(ActualDuration(2, 1)))

    with pytest.raises(TypeError):
        a + 5
    
    with pytest.raises(TypeError):
        a - 5
