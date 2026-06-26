from dataclasses import dataclass
from .MeasureOnset import MeasureOnset
from .Duration import Duration


@dataclass(frozen=True)
class PartOnset:
    """
    Represents a specific point in time, relative to the start of a part.
    This elapsed time is internally represented by a zero-based measure index
    and a `MeasureOnset`. This representation is intentional and aims
    at isolating timing errors within measures. Moreover having a global
    duration onset would become complicated with measures of varying length.
    Moreover, measures in MusicXML don't really have a defined duration,
    they are as long as their musical content and they may overflow/underflow
    even when a time signature is explicitly specified.
    The (measure index, local onset) representation is resilient to all of
    these factors.
    """

    measure_index: int
    """Zero-based measure index. Defines the measure we are currently in.
    Has no connection with measure numbers (XML `number="1"` attributes)."""

    measure_onset: MeasureOnset
    """Local duration-based onset within the current measure."""

    @staticmethod
    def zero_actual(divisions: int) -> "PartOnset":
        """Constructs a zero onset with `ActualDuration` representation"""
        return PartOnset(
            measure_index=0,
            measure_onset=MeasureOnset.zero_actual(divisions)
        )
    
    @staticmethod
    def zero_fractional() -> "PartOnset":
        """Constructs a zero onset with `FractionalDuration` representation"""
        return PartOnset(
            measure_index=0,
            measure_onset=MeasureOnset.zero_fractional()
        )
    
    @staticmethod
    def zero(divisions: int | None) -> "PartOnset":
        """Constructs a zero onset with representation chosen based
        on the provided divisions. If not provided, fractional
        representation is used."""
        if divisions is None:
            return PartOnset.zero_fractional()
        else:
            return PartOnset.zero_actual(divisions)

    def __post_init__(self):
        if self.measure_index < 0:
            raise ValueError("Measure index must be non-negative")

    def __eq__(self, other) -> bool:
        if not isinstance(other, PartOnset):
            return NotImplemented
        return self.measure_index == other.measure_index \
            and self.measure_onset == other.measure_onset

    def __hash__(self) -> int:
        return hash((self.measure_index, self.measure_onset))
    
    def __lt__(self, other) -> bool:
        if not isinstance(other, PartOnset):
            return NotImplemented
        if self.measure_index == other.measure_index:
            return self.measure_onset < other.measure_onset
        return self.measure_index < other.measure_index

    def __le__(self, other) -> bool:
        if not isinstance(other, PartOnset):
            return NotImplemented
        if self.measure_index == other.measure_index:
            return self.measure_onset <= other.measure_onset
        return self.measure_index <= other.measure_index

    def __gt__(self, other) -> bool:
        if not isinstance(other, PartOnset):
            return NotImplemented
        if self.measure_index == other.measure_index:
            return self.measure_onset > other.measure_onset
        return self.measure_index > other.measure_index

    def __ge__(self, other) -> bool:
        if not isinstance(other, PartOnset):
            return NotImplemented
        if self.measure_index == other.measure_index:
            return self.measure_onset >= other.measure_onset
        return self.measure_index >= other.measure_index

    def __add__(self, other) -> "PartOnset":
        # only duration may be added to onset, not another onset
        if not isinstance(other, Duration):
            return NotImplemented
        return PartOnset(
            measure_index=self.measure_index,
            measure_onset=self.measure_onset + other,
        )

    def __radd__(self, other) -> "PartOnset":
        # onset-duration addition is comutative
        return PartOnset.__add__(self, other)

    def __sub__(self, other) -> "Duration":
        if not isinstance(other, PartOnset):
            return NotImplemented
        if self.measure_index != other.measure_index:
            raise ArithmeticError(
                "Only part onsets within the same measure may be subtracted"
            )
        return self.measure_onset - other.measure_onset

    def next_measure(self) -> "PartOnset":
        """Jumps to the next measure, to zero onset.
        Returns this new onset as a new instance."""
        return PartOnset(
            measure_index=self.measure_index + 1,
            measure_onset=MeasureOnset(
                Duration.zero_of_type(self.measure_onset.value)
            )
        )
