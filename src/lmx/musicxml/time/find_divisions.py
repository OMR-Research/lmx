import xml.etree.ElementTree as ET


def find_divisions(element: ET.Element) -> int | None:
    """
    Finds the `<divisions>` value in a given `<part>` element
    or a `<measure>` element and returns it as int.
    If not found, returns None.
    If malformed, raises a ValueError.
    """
    if element.tag not in ["part", "measure"]:
        raise ValueError("Given element is not a <part> nor a <measure>")

    divisions_elements = element.findall(
        ("measure/" if element.tag == "part" else "") + "attributes/divisions"
    )

    if len(divisions_elements) == 0:
        return None
    
    if len(divisions_elements) > 1:
        raise ValueError(
            "Given <part> element contains more than one <divisions> element"
        )
    
    divisions_text = divisions_elements[0].text

    if divisions_text is None:
        raise ValueError(
            "The found <divisions> element does not contain any text"
        )

    return int(divisions_text)
