from lmx.musicxml.time.ActualDuration import ActualDuration
import pytest
from ...assert_xml_equals import assert_xml_equals


def test_it_has_value_equality():
    a = ActualDuration(2, 1)
    b = ActualDuration(4, 1)
    c = ActualDuration(2, 1)
    assert a == a
    assert a != b
    assert a == c
    assert c != b


def test_it_can_be_compared():
    a = ActualDuration(2, 1)
    b = ActualDuration(4, 1)
    assert a < b
    assert a <= b
    assert a <= a
    assert b > a
    assert b >= a
    assert a >= a


def test_it_can_be_added():
    a = ActualDuration(2, 1)
    b = ActualDuration(4, 1)
    c = a + b
    assert c.value == 6
    assert c.divisions == 1


def test_it_can_be_subtracted():
    a = ActualDuration(2, 1)
    b = ActualDuration(4, 1)
    c = b - a
    assert c.value == 2
    assert c.divisions == 1


def test_it_can_be_negated():
    a = ActualDuration(2, 1)
    b = -a
    assert b.value == -2
    assert b.divisions == 1


def test_it_must_have_matching_divisions():
    a = ActualDuration(2, 1)
    b = ActualDuration(4, 2)

    with pytest.raises(ArithmeticError):
        a == b
    
    with pytest.raises(ArithmeticError):
        a + b
    
    with pytest.raises(ArithmeticError):
        a - b
    
    with pytest.raises(ArithmeticError):
        a < b

    with pytest.raises(ArithmeticError):
        a <= b
    
    with pytest.raises(ArithmeticError):
        a > b
    
    with pytest.raises(ArithmeticError):
        a >= b


def test_it_doesnt_support_int_operands():
    a = ActualDuration(2, 1)

    with pytest.raises(TypeError):
        a + 5
    
    with pytest.raises(TypeError):
        a - 5


def test_it_may_be_xml_encoded():
    a = ActualDuration(2, 1)
    assert_xml_equals(
        given=a.to_xml_element(),
        expected="<duration>2</duration>"
    )
