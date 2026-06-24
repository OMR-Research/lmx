import xml.etree.ElementTree as ET
from .normalize_hidden_clefs import ClefSign, ClefRepre, StaffNumber
from .normalize_hidden_clefs import transpose_pitch_for_score_part
import copy
from dataclasses import dataclass
from typing import Literal


# prototyping the API here...


@dataclass(frozen=True)
class Clef:
    """Represents a clef type"""
    
    sign: ClefSign
    """Type of the clef, one of: G, F, C"""

    line: Literal[1, 2, 3, 4, 5]
    """Which staff line the clef sits on, numbered botom up from 1"""


def normalize_invisible_header_clef(
        part_element: ET.Element,
        desired_clef: Clef | list[Clef],
        when_clef_visible: Literal[
            "dont-normalize",
            "normalize-keep-visible",
            "normalize-set-invisible",
            "raise-exception",
        ],
) -> ET.Element:
    """
    Takes in a `<part>` element with invisible header clef and changes
    that clef to the desired clef, while transposing all following notes
    in a way that preserves their visual appearance (staffline positions
    and accidentals). Notes are transposed for until a new visible clef
    is reached. The given `<part>` element typically contains only
    one system, but it isn't required. The '<part>' may contain multiple
    staves (e.g. piano part), in which case each staff behaves
    independently and the desired clef can be specified as a list of clefs
    if each staff is to have a different clef (e.g. [G, F] for piano).

    This method creates a copy of the part element and returns that
    modified copy. The input part element is left unmodified.

    :param part_element: The `<part>` MusicXML element to be normalized.
    :param desired_clef: The clef that should replace the existing
        invisible clef. A list of clefs can be provided for multi-staff
        parts, ordered top to bottom. So for a piano part, you can
        specify desired clefs to be [G, F].
    :param when_clef_visible: Specifies how to behave, when the
        header clef is visible (which is unexpected). Select behaviour
        that best matches your usecase.
    """

    if isinstance(desired_clef, Clef):
        desired_clefs = [desired_clef]
    else:
        desired_clefs = desired_clef
    
    part_element = copy.deepcopy(part_element)
    
    transpose_pitch_for_score_part(
        part_element=part_element,
        staff_count=len(desired_clefs),
        transpose_to=[
            ClefRepre(
                print_object=False,
                staff_number=StaffNumber(i + 1),
                staff_line=dc.line,
                sign=dc.sign,
                octave_change=0
            )
            for i, dc in enumerate(desired_clefs)
        ]
    )
    
    return part_element
