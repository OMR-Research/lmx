from dataclasses import dataclass
from .Duration import Duration
import xml.etree.ElementTree as ET


@dataclass(frozen=True)
class ActualDuration(Duration):
    """Represents a MusicXML `<duration>` value in its actual MusicXML form.
    
    Actual as opposed to fractional, which abstracts away `<divisions>`
    by representing duration with python fractions.
    """

    value: int
    """Duration value in the `<divisions>` unit; i.e how many divisions
    does this duration take up. May be negative, e.g. for `<backup>`s."""

    divisions: int
    """The `<divisions>` value that applies to this duration. It specifies
    how many divisions fit into one quarter note. Actual duration objects
    of different divisions are incompatible."""

    @staticmethod
    def zero(divisions: int) -> "ActualDuration":
        """Constructs a zero duration value"""
        return ActualDuration(0, divisions)

    def __post_init__(self):
        if self.divisions <= 0:
            raise ValueError("Actual duration must have positive divisions")

    def __eq__(self, other) -> bool:
        if not isinstance(other, ActualDuration):
            return NotImplemented
        if self.divisions != other.divisions:
            raise ArithmeticError(
                "Cannot compare actual durations from different divisions contexts"
            )
        return self.value == other.value

    def __hash__(self) -> int:
        # durations of different divisions are unlikely to be placed
        # in the same dictionary
        return hash(self.value)

    def __lt__(self, other) -> bool:
        if not isinstance(other, ActualDuration):
            return NotImplemented
        if self.divisions != other.divisions:
            raise ArithmeticError(
                "Cannot compare actual durations from different divisions contexts"
            )
        return self.value < other.value

    def __le__(self, other) -> bool:
        if not isinstance(other, ActualDuration):
            return NotImplemented
        if self.divisions != other.divisions:
            raise ArithmeticError(
                "Cannot compare actual durations from different divisions contexts"
            )
        return self.value <= other.value

    def __gt__(self, other) -> bool:
        if not isinstance(other, ActualDuration):
            return NotImplemented
        if self.divisions != other.divisions:
            raise ArithmeticError(
                "Cannot compare actual durations from different divisions contexts"
            )
        return self.value > other.value

    def __ge__(self, other) -> bool:
        if not isinstance(other, ActualDuration):
            return NotImplemented
        if self.divisions != other.divisions:
            raise ArithmeticError(
                "Cannot compare actual durations from different divisions contexts"
            )
        return self.value >= other.value

    def __add__(self, other) -> "ActualDuration":
        if not isinstance(other, ActualDuration):
            return NotImplemented
        if self.divisions != other.divisions:
            raise ArithmeticError(
                "Cannot add actual durations from different divisions contexts"
            )
        return ActualDuration(
            value=self.value + other.value,
            divisions=self.divisions
        )

    def __sub__(self, other) -> "ActualDuration":
        if not isinstance(other, ActualDuration):
            return NotImplemented
        if self.divisions != other.divisions:
            raise ArithmeticError(
                "Cannot subtract actual durations from different divisions contexts"
            )
        return ActualDuration(
            value=self.value - other.value,
            divisions=self.divisions
        )

    def __neg__(self) -> "ActualDuration":
        return ActualDuration(
            value=-self.value,
            divisions=self.divisions
        )

    def to_xml_element(self) -> ET.Element:
        """Builds a `<duration>` element that contains this duration."""
        element = ET.Element("duration")
        element.text = str(self.value)
        return element
    
    @staticmethod
    def from_xml_element(
        duration_element: ET.Element,
        divisions: int
    ) -> "ActualDuration":
        """Parses duration from a duration element.
        Divisions must be extracted and provided as argument
        as they are not part of the duration element."""
        assert duration_element.tag == "duration"
        
        if duration_element.attrib.get("fractional", "no") == "yes":
            raise ValueError(
                "Cannot parse actual duration from fractional element"
            )
        
        if duration_element.text is None:
            raise ValueError(
                "Given duration element is missing content"
            )
        
        value = int(duration_element.text)
        
        if value <= 0:
            raise ValueError(
                "Given duration element has negative value, " +
                "which is not allowed by the MusicXML standard"
            )
        
        return ActualDuration(
            value=value,
            divisions=divisions,
        )
