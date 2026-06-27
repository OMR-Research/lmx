from dataclasses import dataclass
from .Duration import Duration
from .ActualDuration import ActualDuration
from .FractionalDuration import FractionalDuration


@dataclass(frozen=True)
class MeasureOnset:
    """
    Represents a specific point in time, relative to the start of a measure.
    This elapsed time is internally represented by a `Duration` object.
    """
    
    value: Duration
    """
    The time that has elapsed since the beginning of the measure
    up until this onset moment, which is being represented by this object.
    """

    @staticmethod
    def zero_actual(divisions: int) -> "MeasureOnset":
        """Constructs a zero onset with `ActualDuration` representation"""
        return MeasureOnset(ActualDuration.zero(divisions))
    
    @staticmethod
    def zero_fractional() -> "MeasureOnset":
        """Constructs a zero onset with `FractionalDuration` representation"""
        return MeasureOnset(FractionalDuration.zero())
    
    @staticmethod
    def zero(divisions: int | None) -> "MeasureOnset":
        """Constructs a zero onset with representation chosen based
        on the provided divisions. If not provided, fractional
        representation is used."""
        if divisions is None:
            return MeasureOnset.zero_fractional()
        else:
            return MeasureOnset.zero_actual(divisions)

    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Onset must be non-negative")

    def __eq__(self, other) -> bool:
        if other == 0:
            return self.value == 0
        if not isinstance(other, MeasureOnset):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)
    
    def __lt__(self, other) -> bool:
        if other == 0:
            return self.value < 0
        if not isinstance(other, MeasureOnset):
            return NotImplemented
        return self.value < other.value

    def __le__(self, other) -> bool:
        if other == 0:
            return self.value <= 0
        if not isinstance(other, MeasureOnset):
            return NotImplemented
        return self.value <= other.value

    def __gt__(self, other) -> bool:
        if other == 0:
            return self.value > 0
        if not isinstance(other, MeasureOnset):
            return NotImplemented
        return self.value > other.value

    def __ge__(self, other) -> bool:
        if other == 0:
            return self.value >= 0
        if not isinstance(other, MeasureOnset):
            return NotImplemented
        return self.value >= other.value

    def __add__(self, other) -> "MeasureOnset":
        # only duration may be added to onset, not another onset
        if not isinstance(other, Duration):
            return NotImplemented
        return MeasureOnset(
            value=self.value + other,
        )

    def __radd__(self, other) -> "MeasureOnset":
        # onset-duration addition is comutative
        return MeasureOnset.__add__(self, other)

    def __sub__(self, other) -> "Duration":
        if not isinstance(other, MeasureOnset):
            return NotImplemented
        return self.value - other.value
