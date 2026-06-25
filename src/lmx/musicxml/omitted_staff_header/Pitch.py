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


@dataclass(frozen=True)
class Pitch:
    step: Step
    alter: int
    octave: int

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
