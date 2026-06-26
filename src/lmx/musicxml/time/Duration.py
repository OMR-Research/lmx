import abc
import xml.etree.ElementTree as ET


class Duration(abc.ABC):
    """Base class for ActualDuration and FractionalDuration"""

    @staticmethod
    def zero_of_type(duration: "Duration") -> "Duration":
        """Returns the zero value of the same duration type as the argument"""
        return duration - duration # a hack that works

    @abc.abstractmethod
    def __lt__(self, other) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def __le__(self, other) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def __gt__(self, other) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def __ge__(self, other) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def __add__(self, other) -> "Duration":
        raise NotImplementedError

    @abc.abstractmethod
    def __sub__(self, other) -> "Duration":
        raise NotImplementedError

    @abc.abstractmethod
    def __neg__(self) -> "Duration":
        raise NotImplementedError

    @abc.abstractmethod
    def to_xml_element(self) -> ET.Element:
        """Builds a `<duration>` element that contains this duration."""
        raise NotImplementedError
