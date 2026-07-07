import xml.etree.ElementTree as ET
from typing import Literal
from ..attributes.get_head_attributes import get_head_attributes


def set_header_clef_visibility(
        part_element: ET.Element,
        set_visibility: Literal["visible", "invisible"],
) -> None:
    """
    Goes through all header clefs and sets their visibility
    to the desired value (regardless of their curent visibility).

    The given part element is modified in-place.

    :param part_element: The part element for which to adjust header clefs.
    :param set_visibility: Whether to set clefs as visible or invisible.
    """
    measure_element = part_element.find("measure")

    if measure_element is None:
        raise ValueError("Given part element contains no measures")

    attributes_element = get_head_attributes(
        measure_element=measure_element,
        create_if_missing=False,
    )

    if attributes_element is None:
        raise ValueError("Given part element does not have header attributes")
    
    for clef_element in attributes_element.findall("clef"):

        # set clef's visibility
        if set_visibility == "visible":
            clef_element.attrib.pop("print-object", None) # ok if missing
        elif set_visibility == "invisible":
            clef_element.attrib["print-object"] = "no"
