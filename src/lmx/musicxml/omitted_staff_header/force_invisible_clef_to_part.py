import xml.etree.ElementTree as ET


def force_invisible_clef_to_part(part_element: ET.Element) -> ET.Element:
    """
    Forces all clefs in the fist list of attributes to be hidden.

    Assumes that clefs with onset zero are located only
    in the first measure in the first list of attributes.
    """
    attrs = part_element.find(".//measure/attributes")
    assert attrs is not None

    for clef_el in attrs.findall("clef"):
        clef_el.set("print-object", "no")
    
    return part_element