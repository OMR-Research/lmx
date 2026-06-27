import xml.etree.ElementTree as ET
from .Pitch import Pitch
from typing import Callable
from ..time.PartOnset import PartOnset
from ..time.OnsetVisitor import OnsetVisitor


def map_part_pitches(
        part_element: ET.Element,
        pitch_mapper: Callable[[ET.Element, Pitch, PartOnset, int], Pitch]
) -> None:
    """
    Utility functor that lets you adjust values of `<pitch>`
    elements in a `<part>` element. The argument mapper function
    receives extracted context for each invoked pitch element.

    The given part element is modified in-place. No value is returned.

    :param part_element: The `<part>` element, whose pitches are to be mapped.
    :param pitch_mapper: The function that will be invoked for each pitch
        and is expected to return the new pitch. It receives these arguments:
        (the parent `<note>` element; the current pitch;
        part-relative onset in divisisons; staff number)
        It must return the new pitch.
    """
    assert part_element.tag == "part", \
        "The given element is not a `<part>`"
    
    class MyVisitor(OnsetVisitor):
        def __init__(self):
            super().__init__(record_onsets=False)
        
        def visit_note(self, note_element: ET.Element):
            # only `<note>` elements have pitches
            # (and skip those that don't)
            pitch_element = note_element.find("pitch")
            if pitch_element is None:
                return
            
            # update pitch
            staff_number = int(note_element.findtext("staff", "1"))
            pitch = Pitch.from_pitch_element(pitch_element)
            new_pitch = pitch_mapper(
                note_element,
                pitch,
                self.part_onset,
                staff_number
            )
            new_pitch.populate_pitch_element(pitch_element)

    MyVisitor().run(part_element)
