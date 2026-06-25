from dataclasses import dataclass
from typing import Literal
import xml.etree.ElementTree as ET
from typing import cast


ClefSign = Literal["G", "F", "C"]
ClefLine = Literal[1, 2, 3, 4, 5]


DEFAULT_LINES_FOR_SIGNS: dict[ClefSign, ClefLine] = {
    "G": 2,
    "F": 4,
    "C": 3,
}


@dataclass(frozen=True)
class Clef:
    """Represents a clef type"""
    
    sign: ClefSign
    """Type of the clef, one of: G, F, C"""

    line: ClefLine
    """Which staff line the clef sits on, numbered botom up from 1"""

    octave_change: int = 0
    """Octave shift built into the clef,
    corresponds to `<clef-octave-change>` element"""

    def __post_init__(self):
        assert self.sign in ["G", "F", "C"]
        assert self.line in [1, 2, 3, 4, 5]
        assert type(self.octave_change) is int

    @staticmethod
    def from_clef_element(clef_element: ET.Element) -> "Clef":
        sign = clef_element.findtext("sign")
        assert sign is not None, \
            "The <sign> element is mandatory but is missing"

        line = int(clef_element.findtext(
            "line",
            str(DEFAULT_LINES_FOR_SIGNS[cast(ClefSign, sign)])
        ))
        octave_change = int(clef_element.findtext("clef-octave-change", "0"))

        assert sign in ["G", "F", "C"]
        assert line in [1, 2, 3, 4, 5]

        return Clef(
            sign=cast(ClefSign, sign),
            line=cast(ClefLine, line),
            octave_change=octave_change,
        )

    def populate_clef_element(
            self,
            clef_element: ET.Element,
            set_visibility: Literal["visible", "invisible"]
    ):
        """Adjusts content of a given `<clef>` element
        to match the represented clef"""

        # adjust <clef> visibility
        if set_visibility == "visible":
            del clef_element.attrib["print-object"]
        elif set_visibility == "invisible":
            clef_element.attrib["print-object"] = "no"

        # sign
        sign_element = clef_element.find("sign")
        if sign_element is None:
            sign_element = ET.Element("sign")
            clef_element.insert(0, sign_element)
        
        sign_element.text = str(self.sign)

        # line
        line_element = clef_element.find("line")
        if line_element is None:
            line_element = ET.Element("line")
            clef_element.insert(1, line_element)
        
        line_element.text = str(self.line)

        # octave change
        octave_element = clef_element.find("clef-octave-change")
        if octave_element is None:
            octave_element = ET.Element("clef-octave-change")
            clef_element.insert(2, octave_element)
        
        octave_element.text = str(self.octave_change)

        # when octave change is 0, the element itself should be missing
        if self.octave_change == 0:
            clef_element.remove(octave_element)
    
    @staticmethod
    def is_element_visible(clef_element: ET.Element) -> bool:
        """Determines, whether an element is visible"""
        return clef_element.attrib.get("print-object", "yes") != "no"


# useful constants
F_CLEF = Clef(sign="F", line=4)
G_CLEF = Clef(sign="G", line=2)
C_CLEF = Clef(sign="C", line=3)
