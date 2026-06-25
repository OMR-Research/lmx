import xml.etree.ElementTree as ET
from .Pitch import Pitch
from typing import Callable


def map_part_pitches(
        part_element: ET.Element,
        pitch_mapper: Callable[[ET.Element, Pitch, int, int], Pitch]
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

    # track onset relative to the start of the part
    part_onset = 0

    for measure_element in part_element.findall("measure"):
        for child in measure_element:
            
            # only `<note>` elements have pitches
            # (and skip those that don't)
            if child.tag == "note":
                note_element = child
                pitch_element = child.find("pitch")
                if pitch_element is not None:

                    # update pitch
                    staff_number = int(note_element.findtext("staff", "1"))
                    pitch = Pitch.from_pitch_element(pitch_element)
                    new_pitch = pitch_mapper(
                        note_element,
                        pitch,
                        part_onset,
                        staff_number
                    )
                    new_pitch.populate_pitch_element(pitch_element)

            # update onset (always)
            duration = int(child.findtext("duration", "0"))
            if child.tag == "backup":
                duration = -duration
            part_onset += duration
