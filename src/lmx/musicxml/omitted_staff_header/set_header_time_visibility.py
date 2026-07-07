import xml.etree.ElementTree as ET
from typing import Literal
from ..attributes.get_head_attributes import get_head_attributes


def set_header_time_visibility(
        part_element: ET.Element,
        set_visibility: Literal["visible", "invisible"],
) -> None:
    """
    Looks at the header time signature and sets its visibility
    to the desired value (regardless of its curent visibility).

    The given part element is modified in-place.

    :param part_element: The part element for which to adjust the header time.
    :param set_visibility: Whether to set time as visible or invisible.
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
    
    for time_element in attributes_element.findall("time"):

        # set key's visibility
        if set_visibility == "visible":
            time_element.attrib.pop("print-object", None) # ok if missing
        elif set_visibility == "invisible":
            time_element.attrib["print-object"] = "no"
