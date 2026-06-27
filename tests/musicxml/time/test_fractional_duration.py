from lmx.musicxml.time.FractionalDuration import FractionalDuration
import pytest
from ...assert_xml_equals import assert_xml_equals
from fractions import Fraction


def test_it_has_value_equality():
    a = FractionalDuration(2)
    b = FractionalDuration(4)
    c = FractionalDuration(2)
    assert a == a
    assert a != b
    assert a == c
    assert c != b


def test_it_can_be_compared():
    a = FractionalDuration(2)
    b = FractionalDuration(4)
    assert a < b
    assert a <= b
    assert a <= a
    assert b > a
    assert b >= a
    assert a >= a


def test_it_can_be_added():
    a = FractionalDuration(2)
    b = FractionalDuration(4)
    c = a + b
    assert c == FractionalDuration(6)


def test_it_can_be_subtracted():
    a = FractionalDuration(2)
    b = FractionalDuration(4)
    c = b - a
    assert c == FractionalDuration(2)


def test_it_can_be_negated():
    a = FractionalDuration(2)
    b = -a
    assert b == FractionalDuration(-2)


def test_it_doesnt_support_int_operands():
    a = FractionalDuration(2)

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
    zero = FractionalDuration(0)
    assert zero == 0
    assert zero >= 0
    assert zero <= 0
    assert 0 == zero
    assert 0 >= zero
    assert 0 <= zero
    
    one = FractionalDuration(1)
    assert one != 0
    assert one > 0
    assert one >= 0
    assert 0 != one
    assert 0 < one
    assert 0 <= one


def test_it_may_be_xml_encoded():
    assert_xml_equals(
        given=FractionalDuration(2).to_xml_element(),
        expected="""<duration fractional="yes">2</duration>"""
    )

    assert_xml_equals(
        given=FractionalDuration(Fraction(1, 3)).to_xml_element(),
        expected="""<duration fractional="yes">1/3</duration>"""
    )
