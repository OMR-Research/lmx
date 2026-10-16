import xml.etree.ElementTree as ET


def sort_direction_element(direction_element: ET.Element):
    """Sorts children in a `<direction>` element"""
    assert direction_element.tag == "direction", \
        "The given element is not a <direction> element"
    tag_order = [
        # https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/direction/
        "direction-type",
        "offset",
        "footnote",
        "level",
        "voice",
        "staff",
        "sound",
        "listening",
    ]
    direction_element[:] = sorted(
        direction_element,
        key=lambda e: tag_order.index(e.tag)
    )
