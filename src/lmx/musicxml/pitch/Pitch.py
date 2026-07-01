from enum import Enum
from dataclasses import dataclass
import xml.etree.ElementTree as ET


class Step(str, Enum):
    """Represents the MusicXML pitch `<step>` value"""
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"
    A = "A"
    B = "B"


_DIATONIC_STEPS: dict[Step, int] = {
    Step.C: 0,
    Step.D: 1,
    Step.E: 2,
    Step.F: 3,
    Step.G: 4,
    Step.A: 5,
    Step.B: 6,
}
_DIATONIC_STEPS_BACKWARDS: dict[int, Step] = {
    i: s for s, i in _DIATONIC_STEPS.items()
}


@dataclass(frozen=True)
class Pitch:
    step: Step
    """Step within an octave (C, D, E, F, G, A, B)"""
    
    octave: int
    """Scientific pitch notation octave (0, 1, 2, 3, 4, ..., 8, 9)"""

    alter: int
    """Semitones alteration (up/down) from the step+octave position"""

    def __post_init__(self):
        assert isinstance(self.step, Step), "Step must be an enum value"
        assert self.octave >= 0 and self.octave <= 9, \
            "Octave value is outside the MusicXML defined range"
    
    @property
    def diatonic_index(self) -> int:
        """Diatonic index combines the octave and step into one integer
        like so: C0 = 0, D0 = 1, ..., C1 = 7, ...
        
        The alter value must be zero, otherwise an error is raised.
        """
        if self.alter != 0:
            raise RuntimeError(
                "Altered pitches cannot be represented by diatonic index"
            )
        return self.octave * 7 + _DIATONIC_STEPS[self.step]
    
    @staticmethod
    def from_diatonic_index(diatonic_index: int) -> "Pitch":
        """Builds a pitch value from its diatonic index representation"""
        octave, step_index = divmod(diatonic_index, 7)
        step = _DIATONIC_STEPS_BACKWARDS[step_index]
        return Pitch(
            step=step,
            octave=octave,
            alter=0,
        )

    @staticmethod
    def from_pitch_element(pitch_element: ET.Element) -> "Pitch":
        """Constructs the Pitch instance from a MusicXML `<pitch>` element"""
        step = pitch_element.findtext("step")
        octave = pitch_element.findtext("octave")

        assert step is not None, "The <pitch> element is missing a <step>"
        assert octave is not None, "The <pitch> element is missing an <octave>"
        
        alter = int(pitch_element.findtext("alter", "0"))

        return Pitch(
            step=Step(step),
            alter=alter,
            octave=int(octave)
        )
    
    def populate_pitch_element(self, pitch_element: ET.Element):
        """Adjusts content of a given `<pitch>` element
        to match the represented pitch"""

        # step
        step_element = pitch_element.find("step")
        if step_element is None:
            step_element = ET.Element("step")
            pitch_element.insert(0, step_element)
        
        step_element.text = str(self.step.value)

        # alter
        alter_element = pitch_element.find("alter")
        if alter_element is None:
            alter_element = ET.Element("alter")
            pitch_element.insert(1, alter_element)
        
        alter_element.text = str(self.alter)

        # when alter is 0, the element itself should be missing
        if self.alter == 0:
            pitch_element.remove(alter_element)

        # octave
        octave_element = pitch_element.find("octave")
        if octave_element is None:
            octave_element = ET.Element("octave")
            pitch_element.insert(2, octave_element)
        
        octave_element.text = str(self.octave)
