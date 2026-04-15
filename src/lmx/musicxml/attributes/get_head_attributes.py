import xml.etree.ElementTree as ET


def get_head_attributes(
        measure_element: ET.Element,
        create_if_missing=False
) -> ET.Element | None:
    """
    Returns the head `<attributes>` element in the `<measure>`.
    Head is the first occurence of the `<attributes>` element,
    that contains divisions, staff count, clefs and signatures.
    """

    _IGNORE = {"print", "barline"}

    position = 0
    for i, child in enumerate(measure_element):
        position = i
        if child.tag in _IGNORE:
            continue
        elif child.tag == "attributes":
            return child
        else:
            # we hit a note/forward/backup or similar content
            break
    
    if create_if_missing:
        attributes_element = ET.Element("attributes")
        measure_element.insert(position, attributes_element)
        return attributes_element
    
    return None
