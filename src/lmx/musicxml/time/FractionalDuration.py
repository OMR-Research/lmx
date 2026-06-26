from .Duration import Duration
from fractions import Fraction
from numbers import Rational
import xml.etree.ElementTree as ET


class FractionalDuration(Duration):
    """Represents a MusicXML `<duration>` value in a python
    fractional form that does not require the `<divisions>` value.
    
    Fractional as opposed to actual, which uses the MusicXML's `<divisions>`
    value for representing duration.
    """
    
    def __init__(self, value: Fraction | Rational | int):
        self._value = Fraction(value)
    
    @property
    def value(self) -> Fraction:
        """Duration value in the number of quarter notes, represented by a
        python fraction so that less than a quarter note (including triplets)
        may be represented."""
        return self._value
    
    @staticmethod
    def zero() -> "FractionalDuration":
        """Constructs a zero duration value"""
        return FractionalDuration(0)

    def __eq__(self, other) -> bool:
        if not isinstance(other, FractionalDuration):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __lt__(self, other) -> bool:
        if not isinstance(other, FractionalDuration):
            return NotImplemented
        return self.value < other.value

    def __le__(self, other) -> bool:
        if not isinstance(other, FractionalDuration):
            return NotImplemented
        return self.value <= other.value

    def __gt__(self, other) -> bool:
        if not isinstance(other, FractionalDuration):
            return NotImplemented
        return self.value > other.value

    def __ge__(self, other) -> bool:
        if not isinstance(other, FractionalDuration):
            return NotImplemented
        return self.value >= other.value

    def __add__(self, other) -> "FractionalDuration":
        if not isinstance(other, FractionalDuration):
            return NotImplemented
        return FractionalDuration(
            self.value + other.value
        )

    def __sub__(self, other) -> "FractionalDuration":
        if not isinstance(other, FractionalDuration):
            return NotImplemented
        return FractionalDuration(
            value=self.value - other.value
        )

    def __neg__(self) -> "FractionalDuration":
        return FractionalDuration(
            value=-self.value
        )

    def to_xml_element(self) -> ET.Element:
        """Builds a `<duration>` element that contains this duration."""
        element = ET.Element("duration", {"fractional": "yes"})
        element.text = str(self.value)
        return element
