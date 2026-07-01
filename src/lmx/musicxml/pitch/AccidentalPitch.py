from dataclasses import dataclass
from .Pitch import Pitch
import xml.etree.ElementTree as ET


@dataclass(frozen=True, eq=True)
class AccidentalPitch:
    """Represents the pitch-position of an accidental in the score,
    which is a tuple (staff number, pitch octave, pitch step). When an
    accidental appears in a measure, it affects all following notes of the
    same pitch, within the same staff - that's why this representation exists.
    It does NOT capture pitch alter, as it isn't relevant in accidental
    positioning. Also, the pitch ocatve and step are represented jointly
    by an absolute diatonic index, which makes it easier to make comparisons."""
    
    staff_number: int
    """Which staff does the accidental sit on (1, 2) (top, bottom).
    Only 1 for single-staff parts."""

    diatonic_index: int
    """Pitch position within the staff, that automatically respects
    clef changes since we use semantic representation instead of visual.
    Diatonic index is the pitch octave and step combined into one number."""

    @staticmethod
    def from_note_element(note_element: ET.Element) -> "AccidentalPitch":
        """Parses the accidental pitch from a `<note>` element.
        This is the pitch of the `<accidental>` that belongs to this note,
        but this method does not care whether an `<accidental>` element
        is present or not, since it's not needed to determine the pitch."""
        assert note_element.tag == "note"
        
        pitch_element = note_element.find("pitch")
        if pitch_element is None:
            raise ValueError("Given <note> element does not have <pitch>")
        
        staff_number = int(note_element.findtext("staff", "1"))
        pitch = Pitch.from_pitch_element(pitch_element)

        pitch_without_alter = Pitch(
            step=pitch.step,
            octave=pitch.octave,
            alter=0
        )
        
        return AccidentalPitch(
            staff_number=staff_number,
            diatonic_index=pitch_without_alter.diatonic_index,
        )
