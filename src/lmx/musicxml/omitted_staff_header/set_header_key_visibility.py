import xml.etree.ElementTree as ET
from typing import Literal
from ..attributes.get_head_attributes import get_head_attributes


def set_header_key_visibility(
        part_element: ET.Element,
        set_visibility: Literal["visible", "invisible"],
) -> None:
    """
    Looks at the header key signature and sets its visibility
    to the desired value (regardless of its curent visibility).

    The given part element is modified in-place.

    :param part_element: The part element for which to adjust the header key.
    :param set_visibility: Whether to set key as visible or invisible.
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
    
    for key_element in attributes_element.findall("key"):

        is_null_signature = key_element.findtext("fifths") == "0"

        # set key's visibility
        if set_visibility == "visible" or is_null_signature:
            key_element.attrib.pop("print-object", None) # ok if missing
        elif set_visibility == "invisible" and not is_null_signature:
            key_element.attrib["print-object"] = "no"
